from pathlib import Path
from unittest import TestCase

from audioarchivist.collection import Collection
from audioarchivist.tests.storage import Storage

storage = Storage()

class TestCollection(TestCase):
    def test_song_collection(self):
        self.maxDiff = None
        filenames = [
            "meta-collections/collection-1/samples-1/test 1.mp3",
            "meta-collections/collection-1/samples-1/test 2.mp3",
            "meta-collections/collection-1/samples-2/test 3.mp3",
            "meta-collections/collection-2/samples-1/test 4.mp3",
            "meta-collections/collection-2/samples-1/test 5.mp3"
        ]

        for filename in filenames:
            storage.tmp("mp3", filename)

        state = CollectionState()
        Collection(storage.tmpFilename("meta-collections/collection-1/samples-1")).process(state.collector, args = MockArgs(False, False))
        self.assertEqual(state.songCount, 4)
        self.assertEqual(state.albumCount, 1)

        self.assertEqual("|".join(state.songs).replace(" ", ""),
            "Test000:collection-1:mp3:32::4:1:Purpley:Test000:prototypes|" +
            "Test000:collection-1:mp3:32::4:1:Purpley:Test000:prototypes|" +
            "Test000:collection-2:mp3:32::4:1:Purpley:Test000:prototypes|" +
            "Test000:collection-2:mp3:32::4:1:Purpley:Test000:prototypes"
        )

        state = CollectionState()
        Collection(storage.tmpFilename("meta-collections/collection-1")).process(state.collector, args = MockArgs(True, False) )

        self.assertEqual("|".join(state.songs).replace(" ", ""),
            "test1:collection-1:mp3:32::4:1:unknown:test1:samples-1|" +
            "test2:collection-1:mp3:32::4:1:unknown:test2:samples-1|" +
            "test4:collection-2:mp3:32::4:1:unknown:test4:samples-1|" +
            "test5:collection-2:mp3:32::4:1:unknown:test5:samples-1|" +
            "test3:collection-1:mp3:32::4:1:unknown:test3:samples-2"
        )

        for filename in filenames:
            storage.tmpRemove(filename)

class MockArgs:
    def __init__(self, byname, albumsonly):
        self.byname = byname
        self.albumsonly = albumsonly

class CollectionState:
    def __init__(self):
        self.albumCount = 0
        self.songCount = 0
        self.songs = []

    def incrementAlbum(self, album):
        print("Album = " + album)
        self.albumCount += 1

    def incrementSong(self):
        self.songCount += 1

    def storeSong(self, song):
        self.incrementSong()
        print(song)
        self.songs.append(song)

    @property
    def collector(self):
        return {
            "album" : self.incrementAlbum,
            "song"  : self.storeSong,
        }
