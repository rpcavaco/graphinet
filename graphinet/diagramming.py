
from math import ceil
from typing import Optional, List, Dict, Union
from collections import namedtuple
from enum import IntEnum

from graphinet.graphinet import DirectedAciclicGraph, BaseGraphNode

Pt = namedtuple("Pt", "x y")

class AxisType(IntEnum):
	NONE = 0
	LINEAR = 2
	QUANTIZED = 4

class MissingValuesDomain(RuntimeError):
	def __init__(self, p_paramname):
		self.paramname = p_paramname
	def __str__(self):
		return f"Axis value domain definition: {self.paramname} is missing"

class NoSuchAxisIndex(RuntimeError):
	def __init__(self, p_is_x, p_idx):
		self.is_x = p_is_x
		self.idx = p_idx
	def __str__(self):
		if self.is_x:
			orient = "X"
		else:
			orient = "Y"
		return f"Invalid {orient} axis index: {self.idx} is missing"

class LayoutAlreadyInited(RuntimeError):
	def __str__(self):
		return f"Layout with one or more axis already"

class InvalidAxisType(RuntimeError):
	def __init__(self, p_type):
		self.the_type = p_type
	def __str__(self):
		return f"Invalid axis type: {self.the_type}"

# class AxisUndefined(RuntimeError):
# 	def __init__(self, p_is_x):
# 		self.is_x = p_is_x
# 	def __str__(self):
# 		if self.is_x:
# 			return f"X axis is not defined, invoke addXXXAxis with axis type option"
# 		else:
# 			return f"Y axis is not defined, invoke addXXXAxis with axis type option"


class ValueOutOfRange(RuntimeError):
	def __init__(self, p_val, p_min, p_max):
		self.val = p_val
		self.min = p_min
		self.max = p_max
	def __str__(self):
		return f"Value {self.val} not in [{self.min}, {self.max}]"

class OuterRim(object):

	def __init__(self, all: Optional[Union[float, int]] = 0, left: Optional[Union[float, int]] = 0, bottom: Optional[Union[float, int]] = 0, right: Optional[Union[float, int]] = 0, top: Optional[Union[float, int]] = 0) -> None:
		if all > 0:
			self.l = all
			self.b = all
			self.r = all
			self.t = all
		else:
			self.l = left
			self.b = bottom
			self.r = right
			self.t = top

class BaseAxis(object):

	def __init__(self, maxspace: int, minspace: Optional[int] = 0) -> None:
		assert maxspace > minspace
		self.minspace = minspace
		self.maxspace = maxspace
		self.minv = None
		self.sizev = None
		self.maxv = None

	def __repr__(self) -> str:
		return f"axis minspace:{self.minspace} maxspace:{self.maxspace} minv:{self.minv} maxv:{self.maxv} size:{self.sizev}"

	def setIdentValuesDomain(self) -> None:
		self.minv = self.minspace
		self.sizev = self.maxspace - self.minspace
		self.maxv = self.maxspace

	def getValuesDomain(self):
		return self.minv, self.maxv

	def getPosition(self, p_rawvalue: Union[float, int], doraise: Optional[bool] = False) -> Union[None, int]:
		raise NotImplementedError()

class LinearAxis(BaseAxis):
	def __repr__(self) -> str:
		return f"Linear {super().__repr__()}"

	def setValuesDomainSize(self, minimum: Union[float, int], size: Union[float, int]) -> None:
		self.minv = minimum
		self.sizev = size
		self.maxv = self.minv + self.sizev

	def setValuesDomain(self, minimum: Union[float, int], maximum: Union[float, int]) -> None:
		assert maximum > minimum
		self.minv = minimum
		self.sizev = maximum - minimum
		self.maxv = maximum

	def getPosition(self, p_rawvalue: Union[float, int], doraise: Optional[bool] = False) -> Union[None, int]:

		DO_PRINT_LOG = False

		ret = None
		if self.minv is None:
			raise MissingValuesDomain("minimum")
		if self.sizev is None:
			raise MissingValuesDomain("size")

		delta = p_rawvalue - self.minv
		if delta < 0 or p_rawvalue > self.maxv:
			if doraise:
				raise ValueOutOfRange(p_rawvalue, self.minv, self.maxv)
		else:
			m = delta / self.sizev
			ret = self.minspace + round(m * (self.maxspace - self.minspace))

			if DO_PRINT_LOG:
				print("m:", m, "delta:", delta, "self.sizev:", self.sizev)
				print("minspace:", self.minspace, "maxspace:", self.maxspace, "deltaspace:", self.maxspace - self.minspace, "fator:", round(m * (self.maxspace - self.minspace)))

		return ret
		
class QuantizedAxis(LinearAxis):

	def __init__(self, maxspace: int, nquantiles: int, minspace: Optional[int]) -> None:
		super().__init__(maxspace, minspace=minspace)
		assert nquantiles > 0, f"nquantiles must be greater than zero: value given {nquantiles}"
		self.nquantiles = nquantiles
		self.qsz = None

	def __repr__(self) -> str:
		return f"Quantized {super().__repr__()}"

	def _calcQSize(self) -> None:
		q = self.sizev / self.nquantiles
		self.qsz = round(q)

	def setValuesDomainSize(self, minimum: Union[float, int], size: Union[float, int]) -> None:
		super().setValuesDomainSize(minimum, size)
		self._calcQSize()

	def setValuesDomain(self, minimum: Union[float, int], maximum: Union[float, int]) -> None:
		super().setValuesDomain(minimum, maximum)
		self._calcQSize()

	def setIdentValuesDomain(self) -> None:
		super().setIdentValuesDomain()
		self._calcQSize()

	def getPositionFromQuantile(self, p_quantile: int, doraise: Optional[bool] = False) -> Union[None, int]:
		"If predefined quantiles are 2, p_quantile values admissible are 0 & 1"

		DO_PRINT_LOG = False

		if p_quantile < 0 or p_quantile >= self.nquantiles:
			raise ValueOutOfRange(p_quantile, 0, self.nquantiles-1)
		ret = None

		if self.minv is None:
			raise MissingValuesDomain("minimum")
		if self.sizev is None:
			raise MissingValuesDomain("size")

		if p_quantile == 0:
			delta = self.qsz / 2.0
		else:
			delta = p_quantile * self.qsz + self.qsz / 2.0

		m = delta / self.sizev
		ret = self.minspace + round(m * (self.maxspace - self.minspace))

		if DO_PRINT_LOG:
			print("m:", m, "delta:", delta, "self.sizev:", self.sizev)
			print("minspace:", self.minspace, "maxspace:", self.maxspace, "deltaspace:", self.maxspace - self.minspace, "fator:", round(m * (self.maxspace - self.minspace)))

		return ret

	def getPosition(self, p_rawvalue: Union[float, int], doraise: Optional[bool] = False) -> Union[None, int]:
		"Quantize value and call getValueAtQuantile"
		assert not self.qsz is None
		testv = p_rawvalue - self.minv
		qnt, rem = divmod(testv, self.qsz)
		if qnt > 0 and rem == 0:
			qnt -= 1
		return self.getPositionFromQuantile(qnt, doraise=doraise)
		

class BaseLayout(object):

	def __init__(self, w: Union[float, int], h: Union[float, int], origin: Optional[Pt] = None) -> None:
		self.width = w		
		self.height = h
		if origin is None:
			self.origin = Pt(0,0)
		else:
			self.origin = origin
		self.outer_rim = None
		self.xaxis = []
		self.yaxis = []
		self.activeXAxis = None
		self.activeYAxis = None

	def __repr__(self) -> str:
		return f"layout width:{self.width} height:{self.height} origin:{self.origin}"

	def setOuterRim(self, p_outer_rim: OuterRim) -> None:
		assert not p_outer_rim is None
		self.outer_rim = p_outer_rim
		del self.xaxis[:]
		del self.yaxis[:]
		self.activeXAxis = None
		self.activeYAxis = None

	def _addAxis(self, is_x: bool, doraise: Optional[bool] = False, 
		newtype: Optional[AxisType] = AxisType.NONE, 
		auxdata: Optional[Dict] = None) -> Union[None, BaseAxis]:

		axisClasses = {
			AxisType.LINEAR: LinearAxis,
			AxisType.QUANTIZED: QuantizedAxis
		}

		ret = None
		if is_x:
			the_axis_ptr = self.xaxis
		else:
			the_axis_ptr = self.yaxis

		if newtype != AxisType.NONE:
			the_class = axisClasses[newtype]
			if is_x:
				if not self.outer_rim is None:
					minspace = self.outer_rim.l + self.origin.x
					maxspace = (self.origin.x + self.width) - self.outer_rim.r
				else:
					minspace = self.origin.x
					maxspace = self.origin.x + self.width
			else:
				if not self.outer_rim is None:
					minspace = self.outer_rim.b + self.origin.y
					maxspace = self.origin.y + self.height - self.outer_rim.t
				else:
					minspace = self.origin.y
					maxspace = self.origin.y + self.height

			if newtype == AxisType.LINEAR:
				the_axis_ptr.append(the_class(maxspace, minspace))
			elif newtype == AxisType.QUANTIZED:
				the_axis_ptr.append(the_class(maxspace, auxdata["quantiles"], minspace))
			else:
				raise NotImplementedError(f"missing implementation for type {newtype}")

			if len(the_axis_ptr) > 0:
				if is_x:
					self.activeXAxis = len(the_axis_ptr) - 1
				else:
					self.activeYAxis = len(the_axis_ptr) - 1
				ret = the_axis_ptr[-1]

		elif doraise:
			raise InvalidAxisType(newtype)

		return ret

	def addLinearXAxis(self, doraise: Optional[bool] = False) -> Union[None, BaseAxis]:
		return self._addAxis(True, doraise=doraise, newtype=AxisType.LINEAR)

	def addLinearYAxis(self, doraise: Optional[bool] = False) -> Union[None, BaseAxis]:
		return self._addAxis(False, doraise=doraise, newtype=AxisType.LINEAR)

	def addQuantizedXAxis(self, nquantiles: int, doraise: Optional[bool] = False) -> Union[None, BaseAxis]:
		return self._addAxis(True, doraise=doraise, newtype=AxisType.QUANTIZED, auxdata={"quantiles": nquantiles})

	def addQuantizedYAxis(self, nquantiles: int, doraise: Optional[bool] = False) -> Union[None, BaseAxis]:
		return self._addAxis(False, doraise=doraise, newtype=AxisType.QUANTIZED, auxdata={"quantiles": nquantiles})

	def basicLinearIdentInit(self, doraise: Optional[bool] = False):
		if len(self.xaxis) > 0 and len(self.xaxis) > 0:
			raise LayoutAlreadyInited()
		if len(self.xaxis) < 1:
			xa = self.addLinearXAxis(doraise=doraise)
			xa.setIdentValuesDomain()
		if len(self.yaxis) < 1:
			ya = self.addLinearYAxis(doraise=doraise)
			ya.setIdentValuesDomain()

	def getXAxis(self, p_axisidx: int, activate: Optional[bool] = False, doraise: Optional[bool] = False) -> BaseAxis:
		ln = len(self.xaxis)
		ret = None
		if ln > 0 and p_axisidx < ln:
			if activate:
				self.activeXAxis = p_axisidx
			ret = self.xaxis[p_axisidx]
		elif doraise:
			raise NoSuchAxisIndex(True, p_axisidx)
		return ret

	def getYAxis(self, p_axisidx: int, activate: Optional[bool] = False, doraise: Optional[bool] = False) -> BaseAxis:
		ln = len(self.yaxis)
		ret = None
		if ln > 0 and p_axisidx < ln:
			if activate:
				self.activeYAxis = p_axisidx
			ret = self.yaxis[p_axisidx]
		elif doraise:
			raise NoSuchAxisIndex(False, p_axisidx)
		return ret

	def getPosition(self, p_pointvalue: Pt, xaxisidx: Optional[int] = None, yaxisidx: Optional[int] = None, doraise: Optional[bool] = False):
		if xaxisidx is None:
			xai = self.activeXAxis
		else:
			xai = xaxisidx
		if yaxisidx is None:
			yai = self.activeYAxis
		else:
			yai = yaxisidx

		xa = self.getXAxis(xai, doraise=doraise)
		ya = self.getYAxis(yai, doraise=doraise)

		ret = None
		if not xa is None and not ya is None:
			ret = (xa.getPosition(p_pointvalue.x, doraise=doraise),
					xa.getPosition(p_pointvalue.y, doraise=doraise))
		
		return ret


if __name__ == "__main__":
	pass