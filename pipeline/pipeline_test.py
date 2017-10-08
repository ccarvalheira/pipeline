import unittest
import operator

import pipeline as pp


class GenericThing(object):
	"Helper class for tests."
	def __init__(self, a, b, c, d=1, e=2):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.e = e

	def to_immutable(self):
		return (self.a,self.b,self.c,self.d,self.e)

	def __eq__(self, o):
		return self.a == o.a and self.b == o.b and self.c == o.c and self.d == o.d and self.e == o.e


class AggregateThing(object):
	def __init__(self, a=1):
		self.a = a
	def __sub__(self, o):
		self.a -= o.a
		return self
	def __add__(self, o):
		self.a += o.a
		return self
	def __eq__(self, o):
		return self.a == o.a

class TestIndividualFunctions(unittest.TestCase):

	def test_apply(self):
		tc = [
			(lambda x: x+1, range(20), range(1,21)),
		]
		for t in tc:
			self.assertEqual([i for i in pp.apply(t[0])(t[1])], t[2])

	def test_exclude(self):
		tc = [
			(lambda x: x < 10, range(20), range(10, 20)),
		]
		for t in tc:
			self.assertEqual([i for i in pp.exclude(t[0])(t[1])], t[2])

	def test_exclude_None(self):
		tc = [
			([None, None, None]+range(10)+[None]+range(10,20)+[None,None], range(20)),
		]
		for t in tc:
			self.assertEqual([i for i in pp.exclude_None(t[0])], t[1])


	def test_keep(self):
		tc = [
			(lambda x: x >= 10, range(20), range(10, 20)),
		]
		for t in tc:
			self.assertEqual([i for i in pp.keep(t[0])(t[1])], t[2])


	def test_project(self):
		tc = [
			(["a", "e"], [GenericThing(a,a,a) for a in range(10)], [(a,2) for a in range(10)]),
			(["b", "c"], [GenericThing(a,a+1,a+2) for a in range(10)], [(x+1,x+2) for x in range(10)]),
		]
		for t in tc:
			self.assertEqual([tuple(i) for i in pp.project(*t[0])(t[1])], t[2])

	def test_kproject(self):
		tc = [
			(["a", "e"], [GenericThing(a,a,a) for a in range(10)], [{"a":a, "e":2} for a in range(10)]),
			(["b", "c"], [GenericThing(a,a+1,a+2) for a in range(10)], [{"b":x+1,"c":x+2} for x in range(10)]),
		]
		for t in tc:
			self.assertEqual([i for i in pp.kproject(*t[0])(t[1])], t[2])
	
	def test_splat(self):
		tc = [
			([(a,a+1,a+2) for a in range(10)], [GenericThing(a,a+1,a+2) for a in range(10)]),
			([(a,a,a,1000) for a in range(10)], [GenericThing(a,a,a,1000) for a in range(10)]),
		]
		for t in tc:
			self.assertEqual([i for i in pp.splat(GenericThing)(t[0])], t[1])

	def test_ksplat(self):
		tc = [
			([{"a":a,"b":a+1,"c":a+2} for a in range(10)], [GenericThing(a,a+1,a+2) for a in range(10)]),
			([{"a":a,"b":a,"c":a,"e":1000} for a in range(10)], [GenericThing(a,a,a,e=1000) for a in range(10)]),
		]
		for t in tc:
			self.assertEqual([i for i in pp.ksplat(GenericThing)(t[0])], t[1])

	def test_materialize(self):
		tc = [
			(range(20), range(20)),
		]
		for t in tc:
			self.assertEqual([i for i in pp.materialize(t[0])], t[1])

	def test_drain(self):
		tc = [
			range(20),
			[],
		]
		for t in tc:
			self.assertEqual([i for i in pp.drain(t)], [])

	def test_unique(self):
		tc = [
			(lambda x: x.to_immutable(), [GenericThing(1,2,3), GenericThing(1,2,3)], [GenericThing(1,2,3)]),
			(None, range(10)+range(10), range(10)), 
		]
		for t in tc:
			self.assertEqual([i for i in pp.unique(t[0])(t[1])], t[2])

	def test_aggregate(self):
		tc = [
			((operator.sub, AggregateThing(1)), [GenericThing(1,2,3), AggregateThing(2), GenericThing(1,2,3)], AggregateThing(-3)),
			((operator.add, AggregateThing(1)), [GenericThing(1,2,3), AggregateThing(2), GenericThing(1,2,3)], AggregateThing(5)),
			((operator.add, 0), range(5), sum(range(5))),
		]
		for t in tc:
			self.assertEqual(pp.aggregate(t[0][0], t[0][1])(t[1]), t[2])


class TestPipelines(unittest.TestCase):

	def test_a_pipeline(self):
		allD = 10000
		p = pp.P(
			range(10) + [None, None] + range(10), 	#initial iterator
			pp.exclude_None, 						#exclude items which are None
			pp.keep(lambda i: i%2 == 0),			#keep even elements
			pp.apply(lambda i: i*2),				#multiply every element by two
			pp.apply(lambda i: (i, i+1, i+2, allD)),#create a tuple with numbers using a variable outside the pipeline 
			pp.splat(GenericThing),					#"cast" tuple to object
			pp.unique(lambda gt: gt.to_immutable()),#remove duplicate objects according to key
			pp.project("a", "b", "e"),				#get tuple with selected attributes
			pp.splat(GenericThing),					#"recast" tuple to objects
			pp.materialize,							#precipitate the processing of the pipeline, returning a list
		)
		self.assertEqual(p, 
			[GenericThing(0, 1, 2), GenericThing(4, 5, 2), GenericThing(8, 9, 2), GenericThing(12, 13, 2), GenericThing(16, 17, 2)]) 