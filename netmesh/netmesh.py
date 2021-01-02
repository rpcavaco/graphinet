 
from queue import PriorityQueue

from typing import Optional, List

PARENT = 0
CHILD = 2

# class TreeError(RuntimeError):
	# def __init__(self, p_msg):
		# self.msg = p_msg
	# def __str__(self):
		# return f"TreeError: {self.msg}"
		
class NotBaseNodeError(RuntimeError):
	def __str__(self):
		return "Not a _NodeSkel/_BaseNode instance"

class NodeAlreadyExists(RuntimeError):
	def __init__(self, p_thisnode, p_othernode, p_reltype: int):
		self.thisid = p_thisnode.id
		self.otherid = p_othernode.id
		self.reltype = p_reltype
	def __str__(self):
		if self.reltype == PARENT:
			ret = f"Node {self.otherid} already marked as parent of id: {self.thisid}"
		else:
			ret = f"Node {self.otherid} already marked as child of id: {self.thisid}"
		return ret

class MissingNodeIDsError(RuntimeError):
	def __init__(self, p_ids):
		self.p_ids = p_ids
	def __str__(self):
		return f"Missing node IDs: {self.p_ids}"

class ExistingNodeIdError(RuntimeError):
	def __init__(self, p_id):
		self.p_id = p_id
	def __str__(self):
		return f"Existing node Id: {self.p_id}"

class CycleAttemptError(RuntimeError):
	def __init__(self, p_ids):
		self.p_ids = p_ids
	def __str__(self):
		return f"Attempt to insert cycle on ids: {self.p_ids}"
				
class ImproperSortingMethod(RuntimeError):
	def __init__(self, p_classname):
		self.p_classname = p_classname
	def __str__(self):
		return f"Method __lt__ for sorting nodes is improperly extended for {self.p_classname}"
		
class _NodeSkel(object):	
	def __init__(self):
		self.parentids = None
		self.childrenids = None
		self.id = None
		
class BaseMeshNode(_NodeSkel):

	def __init__(self, ident=None, parentids: Optional[List[_NodeSkel]] = [], childrenids: Optional[List[_NodeSkel]] = []):
		self.parentids = parentids
		self.childrenids = childrenids
		if ident is None:
			self.id = str(id(self))
		else:
			self.id = ident
			
	def __repr__(self):
		return self.id
		
	def __eq__(self, other):
		return self.id == other.id
		
	def __ne__(self, other):
		return self.id != other.id
		
	def __lt__(self, other):
		"""THIS METHOD SHUOLD BE EXTENDED BY SUBCLASSES, TO PROPER SORT NODES ALONG MESH"""
		return self.id < other.id
			
	def getParentIds(self) -> List[str]:
		return self.parentids

	def getChildIds(self) -> List[str]:
		return self.childrenids
		
	def checkParentExists(self, other: _NodeSkel):
		if other is None or not isinstance(other, _NodeSkel):
			raise NotBaseNodeError()			
		return other.id in self.getParentIds()
		
	def checkChidExists(self, other: _NodeSkel):
		if other is None or not isinstance(other, _NodeSkel):
			raise NotBaseNodeError()			
		return other.id in self.getChildIds()
			
	def addParent(self, other: _NodeSkel):
		if self.checkParentExists(other):
			raise NodeAlreadyExists(self, other, PARENT)
		other.addChild(self)
		self.parentids.append(other.id)

	def addChild(self, other: _NodeSkel):
		if self.checkChidExists(other):
			raise NodeAlreadyExists(self, other, CHILD)
		other.addParent(self)
		self.childrenids.append(other.id)
			
	def addChildren(self, children: List[_NodeSkel]):
		for chld in children:
			self.addChild(chld)
			

class DirectedMesh(object):	
	
	def __init__(self):
		self.rootids = []		
		self.nodes = {}
		
	def checkIDs(self, lids: List[str]):
		if len(lids) < 1:
			return
		tstids = set(lids)
		xstkeys = set(self.nodes.keys())
		if len(xstkeys) > 0 and tstids.isdisjoint(xstkeys):
			raise MissingNodeIDsError(tstids.difference(xstkeys))	
			
	def iterateUp(self, start_ident):
		
		if not start_ident in self.nodes.keys():
			raise MissingNodeIDsError(start_ident)
			
		fringe = PriorityQueue()
		fringed_ids = set()
		lvl = 0
		
		n = self.nodes[start_ident]
		for pid in n.parentids:
			p = self.nodes[pid]
			fringe.put((lvl, p))
			fringed_ids.add(pid)
			
		while not fringe.empty():
			flvl, fn = fringe.get()
			yield fn
			for fpid in fn.parentids:
				if fpid in fringed_ids:
					continue
				fp = self.nodes[fpid]
				try:
					fringe.put((flvl+1, fp))
					fringed_ids.add(fpid)
				except TypeError:
					raise ImproperSortingMethod(str(type(fp)))
		
	def iterateDown(self, start_ident):
		
		if not start_ident in self.nodes.keys():
			raise MissingNodeIDsError(start_ident)
			
		fringe = PriorityQueue()
		fringed_ids = set()
		lvl = 0
		
		n = self.nodes[start_ident]
		for pid in n.childrenids:
			p = self.nodes[pid]
			fringe.put((lvl, p))
			fringed_ids.add(pid)
			
		while not fringe.empty():
			flvl, fn = fringe.get()
			yield fn
			for fpid in fn.childrenids:
				if fpid in fringed_ids:
					continue
				fp = self.nodes[fpid]
				try:
					fringe.put((flvl+1, fp))
					fringed_ids.add(fpid)
				except TypeError:
					raise ImproperSortingMethod(str(type(fp)))
		
	def addNode(self, node: BaseMeshNode):	
		
		if node.id in self.nodes.keys():
			raise ExistingNodeIdError(node.id)
			
		self.checkIDs(node.parentids)
		self.checkIDs(node.childrenids)
		
		#lparents = [self.nodes[pid] for pid in node.parentids]
		#lchildren = [self.nodes[pid] for pid in node.childrenids]

		self.nodes[node.id] = node
		
		if len(node.parentids) == 0:
			# New root
			if len(node.childrenids) > 0:
				roots_to_cancel = set(node.childrenids).intersection(set(self.rootids))
				for rtc in roots_to_cancel:
					self.rootids.remove(rtc)
			self.rootids.append(node.id)
			
		sa = {cid for cid in self.nodes[node.id].childrenids}
		sb = {n.id for n in self.iterateUp(node.id)}
		if len(sa) > 0 and len(sb) > 0 and sa.issubset(sb):
			raise CycleAttemptError(sa.intersection(sb))

		sa = {pid for pid in self.nodes[node.id].parentids}
		sb = {n.id for n in self.iterateDown(node.id)}
		if len(sa) > 0 and len(sb) > 0 and sa.issubset(sb):
			raise CycleAttemptError(sa.intersection(sb))
		
		return self.nodes[node.id]
		

if __name__ == "__main__":
	m = DirectedMesh()
	m.addNode(BaseMeshNode(ident="zeroot"))
	m.addNode(BaseMeshNode(ident="zefilhoa", parentids=["zeroot"]))
	m.addNode(BaseMeshNode(ident="zefilhob", parentids=["zeroot"]))
	m.addNode(BaseMeshNode(ident="zenetob", parentids=["zefilhoa", "zefilhob"]))
	m.addNode(BaseMeshNode(ident="zbisenetob", parentids=["zenetob"]))
	m.addNode(BaseMeshNode(ident="zbisenetoc", parentids=["zenetob"]))
	print("Root ids:", m.rootids)
	print("Nodes:",m.nodes.keys())
	print("Iterate:",list(m.iterateUp("zbisenetoc")))
