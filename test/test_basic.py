
import pytest

from graphinet.graphinet import DirectedAciclicGraph, BaseGraphNode, CycleAttemptError, MissingNodeIDsError

@pytest.fixture()
def prepared_dag():
	m = DirectedAciclicGraph()
	m.addNode(BaseGraphNode(ident="zeroot"))
	m.addNode(BaseGraphNode(ident="zefilhoa", parentids=["zeroot"]))
	m.addNode(BaseGraphNode(ident="zefilhob", parentids=["zeroot"]))
	m.addNode(BaseGraphNode(ident="zenetob", parentids=["zefilhoa", "zefilhob"]))
	m.addNode(BaseGraphNode(ident="zbisenetob", parentids=["zenetob"]))
	m.addNode(BaseGraphNode(ident="zbisenetoc", parentids=["zenetob"]))
	yield m

class TestClass:

	def test_getnode(self, prepared_dag):
		with pytest.raises(MissingNodeIDsError) as e_info:
			prepared_dag.getNode("xafs", doraise=True)
		assert prepared_dag.getNode("xifs") == None
		assert isinstance(prepared_dag.getNode("zenetob"), BaseGraphNode)

	def test_nodeslist(self, prepared_dag):
		assert len(list(prepared_dag.nodes.keys())) == 6

	def test_root(self, prepared_dag):
		assert prepared_dag.rootids == ['zeroot']
		
	def test_nodes(self, prepared_dag):
		assert len(prepared_dag.getNode("zeroot").getParentIds()) == 0
		assert set(prepared_dag.getNode("zeroot").getChildrenIds()) == set(['zefilhoa', 'zefilhob'])

		assert prepared_dag.getNode("zefilhoa").getParentIds() == ["zeroot"]
		assert prepared_dag.getNode("zefilhoa").getChildrenIds() == ["zenetob"]

		assert prepared_dag.getNode("zefilhob").getParentIds() == ["zeroot"]
		assert prepared_dag.getNode("zefilhob").getChildrenIds() == ["zenetob"]

		assert set(prepared_dag.getNode("zenetob").getParentIds()) == set(['zefilhoa', 'zefilhob'])
		assert set(prepared_dag.getNode("zenetob").getChildrenIds()) == set(['zbisenetob', 'zbisenetoc'])

		assert prepared_dag.getNode("zbisenetob").getParentIds() == ['zenetob']
		assert len(prepared_dag.getNode("zbisenetob").getChildrenIds()) == 0

		assert prepared_dag.getNode("zbisenetoc").getParentIds() == ['zenetob']
		assert len(prepared_dag.getNode("zbisenetoc").getChildrenIds()) == 0

	def test_itup(self, prepared_dag):
		assert {n.ident for n in prepared_dag.iterateUp("zbisenetob")} == set(['zbisenetob', 'zenetob', 'zefilhoa', 'zefilhob', 'zeroot'])

	def test_itdwn(self, prepared_dag):
		assert {n.ident for n in prepared_dag.iterateDown("zeroot")} == set(['zeroot', 'zefilhoa', 'zefilhob', 'zenetob', 'zbisenetob', 'zbisenetoc'])

	def test_edge1(self, prepared_dag):
		prepared_dag.addEdge("zeroot", "zenetob", doraise=True)
		assert {n.ident for n in prepared_dag.iterateUp("zbisenetob")} == set(['zbisenetob', 'zenetob', 'zefilhoa', 'zefilhob', 'zeroot'])
		assert set(prepared_dag.getNode("zenetob").getParentIds()) == set(['zeroot','zefilhoa', 'zefilhob'])

	def test_edge2(self, prepared_dag):
		with pytest.raises(CycleAttemptError) as e_info:
			prepared_dag.addEdge("zenetob", "zeroot", doraise=True)
