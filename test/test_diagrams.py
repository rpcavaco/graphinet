
import pytest

from graphinet.diagramming import AxisType, LinearAxis, QuantizedAxis, \
	ValueOutOfRange, BaseLayout, OuterRim, Pt

class TestClass:

	def test_linearaxis(self):
		la = LinearAxis(1000, minspace=100)
		la.setValuesDomainSize(40, 120)
		with pytest.raises(ValueOutOfRange):
			x = la.getValue(12, doraise=True)
		assert la.getValue(12) is None
		assert la.getValue(60) == 250

		la.setValuesDomain(40, 120)
		assert la.getValue(60) == 325

	def test_quantaxis(self):
		qa = QuantizedAxis(1000, 2, minspace=100)
		qa.setValuesDomainSize(40, 120)
		assert qa.getValue(50, doraise=True) == 325
		assert qa.getValueFromQuantile(1, doraise=True) == 775
		with pytest.raises(ValueOutOfRange):
			x = qa.getValueFromQuantile(2, doraise=True)

	#def test_blayout(self, capsys):
	def test_blayout1(self):
		bl = BaseLayout(1000, 800, origin = Pt(10,10))
		bl.setOuterRim(OuterRim(all=10))
		xa = bl.getLinearXAxis(doraise=True)
		xa.setValuesDomain(40, 160)
		assert xa.getValue(80, doraise=True) == 347
		ya = bl.getLinearYAxis(doraise=True)
		ya.setValuesDomain(80, 200)
		assert ya.getValue(100, doraise=True) == 150
		# with capsys.disabled():
		#  	print(ya.getValue(100, doraise=True))

	def test_blayout2(self, capsys):
		bl = BaseLayout(1000, 800, origin = Pt(10,10))
		bl.setOuterRim(OuterRim(all=10))
		xa = bl.getQuantizedXAxis(2, doraise=True)
		xa.setIdentValuesDomain()
		assert xa.getValuesDomain() == (20, 1000)
		assert xa.getValue(100, doraise=True) == 265
		ya = bl.getQuantizedYAxis(3, doraise=True)
		ya.setIdentValuesDomain()
		assert ya.getValuesDomain() == (20, 800)
		assert ya.getValue(620, doraise=True) == 670
		assert ya.getValue(740, doraise=True) == 670
		#with capsys.disabled():
		#	print(ya.getValue(620, doraise=True))
		with pytest.raises(ValueOutOfRange):
			x = ya.getValue(19, doraise=True)
		with pytest.raises(ValueOutOfRange):
			x = ya.getValue(801, doraise=True)

