import time
import unittest
from pubsub import pub
from pubsub.core import topicargspec


class TestController(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.topicMgr = pub.getDefaultTopicMgr()
		cls.topicMgr.delTopic('echo')

	def setUp(self):
		pub.unsubAll()
		self.answer = None

	def tearDown(self):
		self.topicMgr.delTopic('echo')

	def getReply(self):
		#Wait for function to respond
		for i in range(20):
			if (self.answer != None):
				break
			time.sleep(0.01)
		else:
			errorMessage = "No response"
			raise ValueError(errorMessage)

		_answer = self.answer
		self.answer = None
		return _answer

	def test_empty(self):
		def myFunction(): self.answer = -1
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo')
		self.assertEqual(self.getReply(), -1)

		with self.assertRaises(topicargspec.SenderUnknownMsgDataError):
			pub.sendMessage('echo', arg1 = 1)

	def test_allArgs_noDefaults(self):
		def myFunction(arg1, arg2, arg3): self.answer = (arg1, arg2, arg3)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2)

	def test_allArgs_withDefaults(self):
		def myFunction(arg1, arg2, arg3 = 3): self.answer = (arg1, arg2, arg3)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2)
		self.assertEqual(self.getReply(), (1, 2, 3))

		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4))

	def test_allArgs_allDefaults(self):
		def myFunction(arg1 = 1, arg2 = 2, arg3 = 3): self.answer = (arg1, arg2, arg3)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo')
		self.assertEqual(self.getReply(), (1, 2, 3))

		pub.sendMessage('echo', arg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4))

	def test_allArgs_noDefaults_starArgs(self):
		def myFunction(arg1, arg2, arg3, *args): self.answer = (arg1, arg2, arg3, args)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, ()))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2)

	def test_allArgs_withDefaults_starArgs(self):
		def myFunction(arg1, arg2, arg3 = 3, *args): self.answer = (arg1, arg2, arg3, args)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2)
		self.assertEqual(self.getReply(), (1, 2, 3, ()))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4, ()))

	def test_allArgs_noDefaults_starStarKwargs(self):
		def myFunction(arg1, arg2, arg3, **kwargs): self.answer = (arg1, arg2, arg3, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, {}))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2)

	def test_allArgs_withDefaults_starStarKwargs(self):
		def myFunction(arg1, arg2, arg3 = 3, **kwargs): self.answer = (arg1, arg2, arg3, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2)
		self.assertEqual(self.getReply(), (1, 2, 3, {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4, {}))

	def test_allArgs_noDefaults_starArgs_starStarKwargs(self):
		def myFunction(arg1, arg2, arg3, *args, **kwargs): self.answer = (arg1, arg2, arg3, args, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, (), {}))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2)

	def test_allArgs_withDefaults_starArgs_starStarKwargs(self):
		def myFunction(arg1, arg2, arg3 = 3, *args, **kwargs): self.answer = (arg1, arg2, arg3, args, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2)
		self.assertEqual(self.getReply(), (1, 2, 3, (), {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, arg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4, (), {}))

	def test_allKwargs_noDefaults(self):
		def myFunction(*, kwarg1, kwarg2): self.answer = (kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 2)
		self.assertEqual(self.getReply(), (1, 2))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', kwarg1 = 1)

	def test_allKwargs_withDefaults(self):
		def myFunction(*, kwarg1, kwarg2 = 2): self.answer = (kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1)
		self.assertEqual(self.getReply(), (1, 2))
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 3)
		self.assertEqual(self.getReply(), (1, 3))

	def test_allKwargs_allDefaults(self):
		def myFunction(*, kwarg1 = 1, kwarg2 = 2, kwarg3 = 3): self.answer = (kwarg1, kwarg2, kwarg3)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo')
		self.assertEqual(self.getReply(), (1, 2, 3))

		pub.sendMessage('echo', kwarg3 = 4)
		self.assertEqual(self.getReply(), (1, 2, 4))

	def test_allKwargs_noDefaults_starArgs(self):
		def myFunction(*args, kwarg1, kwarg2): self.answer = (args, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 2)
		self.assertEqual(self.getReply(), ((), 1, 2))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', kwarg1 = 1)

	def test_allKwargs_withDefaults_starArgs(self):
		def myFunction(*args, kwarg1, kwarg2 = 2): self.answer = (args, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1)
		self.assertEqual(self.getReply(), ((), 1, 2))
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 3)
		self.assertEqual(self.getReply(), ((), 1, 3))

	def test_allKwargs_noDefaults_starStarKwargs(self):
		def myFunction(*, kwarg1, kwarg2, **kwargs): self.answer = (kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 2)
		self.assertEqual(self.getReply(), (1, 2, {}))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', kwarg1 = 1)

	def test_allKwargs_withDefaults_starStarKwargs(self):
		def myFunction(*, kwarg1, kwarg2 = 2, **kwargs): self.answer = (kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1)
		self.assertEqual(self.getReply(), (1, 2, {}))
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 3)
		self.assertEqual(self.getReply(), (1, 3, {}))

	def test_allKwargs_noDefaults_starArgs_starStarKwargs(self):
		def myFunction(*args, kwarg1, kwarg2, **kwargs): self.answer = (args, kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 2)
		self.assertEqual(self.getReply(), ((), 1, 2, {}))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', kwarg1 = 1)

	def test_allKwargs_withDefaults_starArgs_starStarKwargs(self):
		def myFunction(*args, kwarg1, kwarg2 = 2, **kwargs): self.answer = (args, kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', kwarg1 = 1)
		self.assertEqual(self.getReply(), ((), 1, 2, {}))
		
		pub.sendMessage('echo', kwarg1 = 1, kwarg2 = 3)
		self.assertEqual(self.getReply(), ((), 1, 3, {}))

	def test_args_noDefaults_kwargs_noDefaults(self):
		def myFunction(arg1, arg2, *, kwarg1, kwarg2): self.answer = (arg1, arg2, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, kwarg1 = 3, kwarg2 = 4)
		self.assertEqual(self.getReply(), (1, 2, 3, 4))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2, kwarg1 = 3)

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 4)

	def test_args_withDefaults_kwargs_noDefaults(self):
		def myFunction(arg1, arg2 = 2, *, kwarg1, kwarg2): self.answer = (arg1, arg2, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 4)
		self.assertEqual(self.getReply(), (1, 2, 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3, kwarg2 = 4)
		self.assertEqual(self.getReply(), (1, 5, 3, 4))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, arg2 = 2, kwarg1 = 3)

	def test_args_noDefaults_kwargs_withDefaults(self):
		def myFunction(arg1, arg2, *, kwarg1, kwarg2 = 4): self.answer = (arg1, arg2, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 2, kwarg1 = 3, kwarg2 = 5)
		self.assertEqual(self.getReply(), (1, 2, 3, 5))

		with self.assertRaises(topicargspec.SenderMissingReqdMsgDataError):
			pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 5)

	def test_args_withDefaults_kwargs_withDefaults(self):
		def myFunction(arg1, arg2 = 2, *, kwarg1, kwarg2 = 4): self.answer = (arg1, arg2, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 5)
		self.assertEqual(self.getReply(), (1, 2, 3, 5))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 5, 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3, kwarg2 = 6)
		self.assertEqual(self.getReply(), (1, 5, 3, 6))

	def test_args_withDefaults_kwargs_withDefaults_starArgs(self):
		def myFunction(arg1, arg2 = 2, *args, kwarg1, kwarg2 = 4): self.answer = (arg1, arg2, args, kwarg1, kwarg2)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 2, (), 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 5)
		self.assertEqual(self.getReply(), (1, 2, (), 3, 5))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 5, (), 3, 4))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3, kwarg2 = 6)
		self.assertEqual(self.getReply(), (1, 5, (), 3, 6))

	def test_args_withDefaults_kwargs_withDefaults_starStarKwargs(self):
		def myFunction(arg1, arg2 = 2, *, kwarg1, kwarg2 = 4, **kwargs): self.answer = (arg1, arg2, kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 2, 3, 4, {}))
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 5)
		self.assertEqual(self.getReply(), (1, 2, 3, 5, {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 5, 3, 4, {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3, kwarg2 = 6)
		self.assertEqual(self.getReply(), (1, 5, 3, 6, {}))

	def test_args_withDefaults_kwargs_withDefaults_starArgs_starStarKwargs(self):
		def myFunction(arg1, arg2 = 2, *args, kwarg1, kwarg2 = 4, **kwargs): self.answer = (arg1, arg2, args, kwarg1, kwarg2, kwargs)
		pub.subscribe(myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 2, (), 3, 4, {}))
		
		pub.sendMessage('echo', arg1 = 1, kwarg1 = 3, kwarg2 = 5)
		self.assertEqual(self.getReply(), (1, 2, (), 3, 5, {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3)
		self.assertEqual(self.getReply(), (1, 5, (), 3, 4, {}))
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 5, kwarg1 = 3, kwarg2 = 6)
		self.assertEqual(self.getReply(), (1, 5, (), 3, 6, {}))

	def test_classMethod(self):
		class myClass():
			def __init__(self, parent):
				self.parent = parent
			def myFunction(self, arg1, arg2 = 2): self.parent.answer = (self, arg1, arg2)
		myObject = myClass(self)
		pub.subscribe(myObject.myFunction, 'echo')
		
		pub.sendMessage('echo', arg1 = 1, arg2 = 3)
		reply = self.getReply()

		self.assertEqual(reply[1:], (1, 3))
		self.assertIsInstance(reply[0], myClass)
					
if __name__ == '__main__':
	unittest.main()
