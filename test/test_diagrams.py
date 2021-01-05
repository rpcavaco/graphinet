
import pytest

from graphinet.diagramming import AxisType, LinearAxis, QuantizedAxis, \
	ValueOutOfRange, BaseLayout, OuterRim, Pt

class TestClass:

	def test_linearaxis(self):
		la = LinearAxis(1000, minspace=100)
		la.setValuesDomainSize(40, 120)
		with pytest.raises(ValueOutOfRange):
			x = la.getPosition(12, doraise=True)
		assert la.getPosition(12) is None
		assert la.getPosition(60) == 250

		la.setValuesDomain(40, 120)
		assert la.getPosition(60) == 325

	def test_quantaxis(self):
		qa = QuantizedAxis(1000, 2, minspace=100)
		qa.setValuesDomainSize(40, 120)
		assert qa.getPosition(50, doraise=True) == 325
		assert qa.getPositionFromQuantile(1, doraise=True) == 775
		with pytest.raises(ValueOutOfRange):
			x = qa.getPositionFromQuantile(2, doraise=True)

	#def test_blayout(self, capsys):
	def test_blayout1(self):
		bl = BaseLayout(1000, 800, origin = Pt(10,10))
		bl.setOuterRim(OuterRim(all=10))
		xa = bl.addLinearXAxis(doraise=True)
		xa.setValuesDomain(40, 160)
		assert xa.getPosition(80, doraise=True) == 347
		ya = bl.addLinearYAxis(doraise=True)
		ya.setValuesDomain(80, 200)
		assert ya.getPosition(100, doraise=True) == 150
		# with capsys.disabled():
		#  	print(ya.getPosition(100, doraise=True))

	def test_blayout2(self, capsys):
		bl = BaseLayout(1000, 800, origin = Pt(10,10))
		bl.setOuterRim(OuterRim(all=10))
		xa = bl.addQuantizedXAxis(2, doraise=True)
		xa.setIdentValuesDomain()
		assert xa.getValuesDomain() == (20, 1000)
		assert xa.getPosition(100, doraise=True) == 265
		ya = bl.addQuantizedYAxis(3, doraise=True)
		ya.setIdentValuesDomain()
		assert ya.getValuesDomain() == (20, 800)
		assert ya.getPosition(620, doraise=True) == 670
		assert ya.getPosition(740, doraise=True) == 670
		#with capsys.disabled():
		#	print(ya.getPosition(620, doraise=True))
		with pytest.raises(ValueOutOfRange):
			x = ya.getPosition(19, doraise=True)
		with pytest.raises(ValueOutOfRange):
			x = ya.getPosition(801, doraise=True)

	def test_blayout3(self): #, capsys):
		bl = BaseLayout(1200, 700)
		#with capsys.disabled():
		bl.basicLinearIdentInit(doraise=True)
		assert bl.getPosition(Pt(20, 400), doraise=True) == (20, 400)

