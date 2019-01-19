class PipelineOp:
	"""
	Pipeline Operations
	Pipeline operations are the principle driving force for any data analysis project. Each implementation of
	`PipelineOp` is a modular, reusable algorithm which performs a single operation. `PipelineOp` has a simple
	interface with only a few conditions necessary to satisfy the contract:

	1. Declare a constructor with inputs necessary to perform the operation in `#perform`.
	2. Implement `#perform`
		This method must return `self`. This provides support to perform the op and immediately assign the call to
		`#output` to local variables.

		Declare op output by calling `#_apply_output` once you've performed your operation.
	"""

	def __init__(self):
		self.__output = None

	def perform(self):
		raise NotImplementedError

	def output(self):
		if self.__output is None:
			self.perform()
		return self.__output

	def _apply_output(self, value):
		self.__output = value
		return self
