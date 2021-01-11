
from os.path import join as path_join

from graphinet.diagramming import AxisType, LinearAxis, QuantizedAxis, \
	ValueOutOfRange, BaseLayout, OuterRim, Pt

from rpcbSVG.SVGLib import BasicDocSVG
from rpcbSVG.SVGstyle import Stroke, Fill
from rpcbSVG.BasicGeom import list2AbsPolylinePath

def test_first(): #capsys):

    bl = BaseLayout(1000, 800)
    bl.setOuterRim(OuterRim(all=20))
    xa = bl.addQuantizedXAxis(10)
    xa.setIdentValuesDomain()
    ya = bl.addQuantizedYAxis(4, invert=True)
    ya.setIdentValuesDomain()

    sdoc = BasicDocSVG(*bl.getDims())
    sdoc.addStyle('circle', Stroke('blue', w=3))
    sdoc.addStyle('path', Fill())
    sdoc.addStyle('circle', Fill('red'))   

    ptlst = (Pt(0,0), Pt(1,1), Pt(2,1), Pt(3,2), Pt(4,0), Pt(5,1), Pt(6,1), Pt(7,2), Pt(8,2), Pt(9,3))
    clrs = ("green", "red", "white", "blue", "orange", "yellow")

    trptlst = [bl.getPosition(pt, fromquantile = True, doraise=True) for pt in ptlst]
    pi = sdoc.addPath(list2AbsPolylinePath(trptlst))
    pid0str = pi.get('id')
    sdoc.addStyle(f"#{pid0str}", Stroke('#7f7b9f', w=8))

    pi1 = sdoc.addPath(list2AbsPolylinePath(trptlst))
    pid1str = pi1.get('id')
    sdoc.addStyle(f"#{pid1str}", Stroke('#8f89c2', w=6))

    pi2 = sdoc.addPath(list2AbsPolylinePath(trptlst))
    pid2str = pi2.get('id')
    sdoc.addStyle(f"#{pid2str}", Stroke('#c4bfef', w=3))

    #with capsys.disabled():
    for idx in range(len(trptlst)):
        pt = trptlst[idx]
        clr = clrs[idx % len(clrs)]
        # print(idx, idx % 6, clr)
        ci = sdoc.addCircle(*pt, 10)
        idstr = ci.get('id')
        sdoc.addStyle(f"#{idstr}", Fill(clr))

    with open(path_join("outtest", 'teste.svg'), 'w') as fl:
        fl.write(sdoc.toString())