"""Tests for SeqIO TwoBitIO module."""


import os
import random
import unittest

from Bio.Seq import Seq, MutableSeq, UndefinedSequenceError
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO


class Parsing(unittest.TestCase):
    """Test parsing 2bit files."""

    def setUp(self):
        path = "TwoBit/sequence.fa"
        records = SeqIO.parse(path, "fasta")
        self.records = list(records)

    def test_littleendian(self, step=5):
        path = "TwoBit/sequence.littleendian.2bit"
        with open(path, "rb") as stream:
            records = SeqIO.parse(stream, "twobit")
            self.assertEqual(records.byteorder, "little")
            self.assertEqual(len(self.records), len(records))
            for record1, record2 in zip(self.records, records):
                self.assertEqual(record1.id, record2.id)
                seq1 = record1.seq
                seq2 = record2.seq
                self.assertEqual(seq1, seq2)
                n = len(seq1)
                for i in range(0, n, step):
                    for j in range(i, n, step):
                        self.assertEqual(seq1[i:j], seq2[i:j])
                        self.assertEqual(repr(seq1[i:j]), repr(seq2[i:j]))

    def test_bigendian(self, step=5):
        path = "TwoBit/sequence.bigendian.2bit"
        with open(path, "rb") as stream:
            records = SeqIO.parse(stream, "twobit")
            self.assertEqual(len(records), 6)
            self.assertEqual(records.byteorder, "big")
            for record1, record2 in zip(self.records, records):
                self.assertEqual(record1.id, record2.id)
                seq1 = record1.seq
                seq2 = record2.seq
                self.assertEqual(seq1, seq2)
                n = len(seq1)
                for i in range(0, n, step):
                    for j in range(i, n, step):
                        self.assertEqual(seq1[i:j], seq2[i:j])
                        self.assertEqual(repr(seq1[i:j]), repr(seq2[i:j]))

    def test_sequence_long(self):
        path = "TwoBit/sequence.long.2bit"
        with open(path, "rb") as stream:
            with self.assertRaises(ValueError) as cm:
                SeqIO.parse(stream, "twobit")
            self.assertEqual(
                str(cm.exception),
                "version-1 twoBit files with 64-bit offsets for index are currently not supported",
            )


class TestComparisons(unittest.TestCase):
    """Test comparisons of sequences read from 2bit files to Seq and other objects."""

    def setUp(self):
        path = "TwoBit/sequence.bigendian.2bit"
        self.stream = open(path, "rb")
        records = SeqIO.parse(self.stream, "twobit")
        record1 = next(records)
        record2 = next(records)
        self.seq1a = record1.seq
        self.seq2a = record2.seq
        path = "TwoBit/sequence.fa"
        records = SeqIO.parse(path, "fasta")
        record1 = next(records)
        record2 = next(records)
        self.seq1b = record1.seq
        self.seq2b = record2.seq

    def tearDown(self):
        self.stream.close()

    def test_eq(self):
        seq1a = self.seq1a
        seq2a = self.seq2a
        seq1b = self.seq1b
        seq2b = self.seq2b
        self.assertEqual(seq1a, seq1b)
        self.assertEqual(seq2a, seq2b)
        self.assertEqual(seq1a, seq1a)
        self.assertEqual(seq2a, seq2a)
        with self.assertRaises(UndefinedSequenceError):
            seq1a == Seq(None, len(seq1a))
        with self.assertRaises(UndefinedSequenceError):
            seq2a == Seq(None, len(seq2a))
        with self.assertRaises(UndefinedSequenceError):
            seq1a == Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2a == Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, len(seq1a)) == seq1a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, len(seq2a)) == seq2a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, 10) == seq1a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, 10) == seq2a

    def test_ne(self):
        seq1a = self.seq1a
        seq2a = self.seq2a
        seq1b = self.seq1b
        seq2b = self.seq2b
        self.assertNotEqual(seq1a, seq2a)
        self.assertNotEqual(seq1a, seq2b)
        with self.assertRaises(UndefinedSequenceError):
            seq1a != Seq(None, len(seq1a))
        with self.assertRaises(UndefinedSequenceError):
            seq2a != Seq(None, len(seq2a))
        with self.assertRaises(UndefinedSequenceError):
            seq1a != Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2a != Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, len(seq1a)) != seq1a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, len(seq2a)) != seq2a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, 10) != seq1a
        with self.assertRaises(UndefinedSequenceError):
            Seq(None, 10) != seq2a

    def test_lt(self):
        seq1 = self.seq1a
        seq2 = self.seq2a
        self.assertLess(seq1, seq2)
        self.assertLess("AA", seq1)
        self.assertLess(seq1, "TT")
        self.assertLess("AA", seq2)
        self.assertLess(seq2, "TTT")
        self.assertLess(b"AA", seq1)
        self.assertLess(seq1, b"TT")
        self.assertLess(b"AA", seq2)
        self.assertLess(seq2, b"TTT")
        self.assertLess(Seq("AA"), seq1)
        self.assertLess(seq1, Seq("TT"))
        self.assertLess(Seq("AA"), seq2)
        self.assertLess(seq2, Seq("TTT"))
        self.assertLess(MutableSeq("AA"), seq1)
        self.assertLess(seq1, MutableSeq("TT"))
        self.assertLess(MutableSeq("AA"), seq2)
        self.assertLess(seq2, MutableSeq("TTT"))
        with self.assertRaises(UndefinedSequenceError):
            seq1 < Seq(None, len(seq1))
        with self.assertRaises(UndefinedSequenceError):
            seq2 < Seq(None, len(seq2))
        with self.assertRaises(UndefinedSequenceError):
            seq1 < Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2 < Seq(None, 10)

    def test_le(self):
        seq1 = self.seq1a
        seq2 = self.seq2a
        self.assertLessEqual(seq1, seq2)
        self.assertLessEqual(seq1, "TT")
        self.assertLessEqual("TT", seq2)
        self.assertLessEqual(seq1, b"TT")
        self.assertLessEqual("TT", seq2)
        self.assertLessEqual(seq1, Seq("TT"))
        self.assertLessEqual("TT", seq2)
        self.assertLessEqual(seq1, MutableSeq("TT"))
        self.assertLessEqual(MutableSeq("TT"), seq2)
        self.assertLessEqual("AA", seq1)
        self.assertLessEqual("AA", seq2)
        self.assertLessEqual(b"AA", seq1)
        self.assertLessEqual(b"AA", seq2)
        self.assertLessEqual(Seq("AA"), seq1)
        self.assertLessEqual(Seq("AA"), seq2)
        self.assertLessEqual(MutableSeq("AA"), seq1)
        self.assertLessEqual(MutableSeq("AA"), seq2)
        self.assertLessEqual("GC", seq1)
        self.assertLessEqual("GC", seq2)
        self.assertLessEqual(b"GC", seq1)
        self.assertLessEqual(b"GC", seq2)
        self.assertLessEqual(Seq("GC"), seq1)
        self.assertLessEqual(Seq("GC"), seq2)
        self.assertLessEqual(MutableSeq("GC"), seq1)
        self.assertLessEqual(MutableSeq("GC"), seq2)
        with self.assertRaises(UndefinedSequenceError):
            seq1 <= Seq(None, len(seq1))
        with self.assertRaises(UndefinedSequenceError):
            seq2 <= Seq(None, len(seq2))
        with self.assertRaises(UndefinedSequenceError):
            seq1 <= Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2 <= Seq(None, 10)

    def test_gt(self):
        seq1 = self.seq1a
        seq2 = self.seq2a
        self.assertGreater(seq2, seq1)
        self.assertGreater("TT", seq1)
        self.assertGreater(seq2, "TT")
        self.assertGreater(b"TT", seq1)
        self.assertGreater(seq2, b"TT")
        self.assertGreater(Seq("TT"), seq1)
        self.assertGreater(seq2, Seq("TT"))
        self.assertGreater(MutableSeq("TT"), seq1)
        self.assertGreater(seq2, MutableSeq("TT"))
        self.assertGreater(seq1, "AA")
        self.assertGreater(seq2, "AA")
        self.assertGreater(seq1, b"AA")
        self.assertGreater(seq2, b"AA")
        self.assertGreater(seq1, Seq("AA"))
        self.assertGreater(seq2, Seq("AA"))
        self.assertGreater(seq1, MutableSeq("AA"))
        self.assertGreater(seq2, MutableSeq("AA"))
        self.assertGreater(seq1, "GC")
        self.assertGreater(seq2, "GC")
        self.assertGreater(seq1, b"GC")
        self.assertGreater(seq2, b"GC")
        self.assertGreater(seq1, Seq("GC"))
        self.assertGreater(seq2, Seq("GC"))
        self.assertGreater(seq1, MutableSeq("GC"))
        self.assertGreater(seq2, MutableSeq("GC"))
        with self.assertRaises(UndefinedSequenceError):
            seq1 > Seq(None, len(seq1))
        with self.assertRaises(UndefinedSequenceError):
            seq2 > Seq(None, len(seq2))
        with self.assertRaises(UndefinedSequenceError):
            seq1 > Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2 > Seq(None, 10)

    def test_ge(self):
        seq1 = self.seq1a
        seq2 = self.seq2a
        self.assertGreaterEqual(seq2, seq1)
        self.assertGreaterEqual("TT", seq1)
        self.assertGreaterEqual(seq2, "TT")
        self.assertGreaterEqual(b"TT", seq1)
        self.assertGreaterEqual(seq2, b"TT")
        self.assertGreaterEqual(Seq("TT"), seq1)
        self.assertGreaterEqual(seq2, Seq("TT"))
        self.assertGreaterEqual(MutableSeq("TT"), seq1)
        self.assertGreaterEqual(seq2, MutableSeq("TT"))
        self.assertGreaterEqual(seq1, "AA")
        self.assertGreaterEqual(seq2, "AA")
        self.assertGreaterEqual(seq1, b"AA")
        self.assertGreaterEqual(seq2, b"AA")
        self.assertGreaterEqual(seq1, Seq("AA"))
        self.assertGreaterEqual(seq2, Seq("AA"))
        self.assertGreaterEqual(seq1, MutableSeq("AA"))
        self.assertGreaterEqual(seq2, MutableSeq("AA"))
        self.assertGreaterEqual(seq1, "GC")
        self.assertGreaterEqual(seq2, "GC")
        self.assertGreaterEqual(seq1, b"GC")
        self.assertGreaterEqual(seq2, b"GC")
        self.assertGreaterEqual(seq1, Seq("GC"))
        self.assertGreaterEqual(seq2, Seq("GC"))
        self.assertGreaterEqual(seq1, MutableSeq("GC"))
        self.assertGreaterEqual(seq2, MutableSeq("GC"))
        with self.assertRaises(UndefinedSequenceError):
            seq1 >= Seq(None, len(seq1))
        with self.assertRaises(UndefinedSequenceError):
            seq2 >= Seq(None, len(seq2))
        with self.assertRaises(UndefinedSequenceError):
            seq1 >= Seq(None, 10)
        with self.assertRaises(UndefinedSequenceError):
            seq2 >= Seq(None, 10)


class TestBaseClassMethods(unittest.TestCase):
    """Test if methods from the base class are called correctly."""

    def setUp(self):
        path = "TwoBit/sequence.bigendian.2bit"
        self.stream = open(path, "rb")
        records = SeqIO.parse(self.stream, "twobit")
        record = next(records)
        self.seq1 = record.seq
        path = "TwoBit/sequence.fa"
        records = SeqIO.parse(path, "fasta")
        record = next(records)
        self.seq2 = record.seq

    def tearDown(self):
        self.stream.close()

    def test_bytes(self):
        b = bytes(self.seq1)
        self.assertIsInstance(b, bytes)
        self.assertEqual(len(b), 480)
        self.assertEqual(b, bytes(self.seq2))
        b = bytes(self.seq1[:10])
        self.assertEqual(len(b), 10)
        self.assertIsInstance(b, bytes)
        self.assertEqual(b, b"GTATACCCCT")

    def test_hash(self):
        self.assertEqual(hash(self.seq1), hash(self.seq2))

    def test_add(self):
        self.assertIsInstance(self.seq1 + "ABCD", Seq)
        self.assertEqual(self.seq1 + "ABCD", self.seq2 + "ABCD")

    def test_radd(self):
        self.assertIsInstance("ABCD" + self.seq1, Seq)
        self.assertEqual("ABCD" + self.seq1, "ABCD" + self.seq2)

    def test_mul(self):
        self.assertIsInstance(2 * self.seq1, Seq)
        self.assertEqual(2 * self.seq1, 2 * self.seq2)
        self.assertIsInstance(self.seq1 * 2, Seq)
        self.assertEqual(self.seq1 * 2, self.seq2 * 2)

    def test_contains(self):
        for seq in (self.seq1, self.seq2):
            self.assertIn("ACCCCT", seq)
            self.assertNotIn("ACGTACGT", seq)

    def test_repr(self):
        self.assertIsInstance(repr(self.seq1), str)
        self.assertEqual(repr(self.seq1), repr(self.seq2))

    def test_str(self):
        self.assertIsInstance(str(self.seq1), str)
        self.assertEqual(str(self.seq1), str(self.seq2))

    def test_count(self):
        self.assertEqual(self.seq1.count("CT"), self.seq2.count("CT"))
        self.assertEqual(self.seq1.count("CT", 75), self.seq2.count("CT", 75))
        self.assertEqual(
            self.seq1.count("CT", 125, 250), self.seq2.count("CT", 125, 250)
        )

    def test_find(self):
        self.assertEqual(self.seq1.find("CT"), self.seq2.find("CT"))
        self.assertEqual(self.seq1.find("CT", 75), self.seq2.find("CT", 75))
        self.assertEqual(self.seq1.find("CT", 75, 100), self.seq2.find("CT", 75, 100))
        self.assertEqual(
            self.seq1.find("CT", None, 100), self.seq2.find("CT", None, 100)
        )

    def test_rfind(self):
        self.assertEqual(self.seq1.rfind("CT"), self.seq2.rfind("CT"))
        self.assertEqual(self.seq1.rfind("CT", 450), self.seq2.rfind("CT", 450))
        self.assertEqual(
            self.seq1.rfind("CT", None, 100), self.seq2.rfind("CT", None, 100)
        )
        self.assertEqual(self.seq1.rfind("CT", 75, 100), self.seq2.rfind("CT", 75, 100))

    def test_index(self):
        self.assertEqual(self.seq1.index("CT"), self.seq2.index("CT"))
        self.assertEqual(self.seq1.index("CT", 75), self.seq2.index("CT", 75))
        self.assertEqual(
            self.seq1.index("CT", None, 100), self.seq2.index("CT", None, 100)
        )
        for seq in (self.seq1, self.seq2):
            self.assertRaises(ValueError, seq.index, "CT", 75, 100)

    def test_rindex(self):
        self.assertEqual(self.seq1.rindex("CT"), self.seq2.rindex("CT"))
        self.assertEqual(
            self.seq1.rindex("CT", None, 100), self.seq2.rindex("CT", None, 100)
        )
        for seq in (self.seq1, self.seq2):
            self.assertRaises(ValueError, seq.rindex, "CT", 450)
            self.assertRaises(ValueError, seq.rindex, "CT", 75, 100)

    def test_startswith(self):
        for seq in (self.seq1, self.seq2):
            self.assertTrue(seq.startswith("GTAT"))
            self.assertTrue(seq.startswith("TGGG", start=10))
            self.assertTrue(seq.startswith("TGGG", start=10, end=14))
            self.assertFalse(seq.startswith("TGGG", start=10, end=12))

    def test_endswith(self):
        for seq in (self.seq1, self.seq2):
            self.assertTrue(seq.endswith("ACCG"))
            self.assertTrue(seq.endswith("ACCG", 476))
            self.assertTrue(seq.endswith("GCAC", 472, 478))
            self.assertFalse(seq.endswith("GCAC", 476, 478))

    def test_split(self):
        self.assertEqual(self.seq1.split(), self.seq2.split())
        self.assertEqual(self.seq1.split("C"), self.seq2.split("C"))
        self.assertEqual(self.seq1.split("C", 1), self.seq2.split("C", 1))

    def test_rsplit(self):
        self.assertEqual(self.seq1.rsplit(), self.seq2.rsplit())
        self.assertEqual(self.seq1.rsplit("C"), self.seq2.rsplit("C"))
        self.assertEqual(self.seq1.rsplit("C", 1), self.seq2.rsplit("C", 1))

    def test_strip(self):
        self.assertEqual(self.seq1.strip("G"), self.seq2.strip("G"))

    def test_lstrip(self, chars=None):
        self.assertEqual(self.seq1.lstrip("G"), self.seq2.lstrip("G"))

    def test_rstrip(self, chars=None):
        self.assertEqual(self.seq1.rstrip("G"), self.seq2.rstrip("G"))

    def test_upper(self):
        self.assertEqual(self.seq1.upper(), self.seq2.upper())

    def test_lower(self):
        self.assertEqual(self.seq1.lower(), self.seq2.lower())

    def test_replace(self):
        # seq.transcribe uses seq._data.replace
        self.assertEqual(self.seq1.transcribe(), self.seq2.transcribe())

    def test_translate(self):
        # seq.complement uses seq._data.translate
        self.assertEqual(self.seq1.complement(), self.seq2.complement())


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
