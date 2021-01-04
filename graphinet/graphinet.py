 
from queue import PriorityQueue

from typing import Optional, List, Union

PARENT = 0
CHILD = 2

class NotBaseNodeError(RuntimeError):
	def __str__(self):
		return "Not a BaseNode instance"

# class NodeAlreadyExists(RuntimeError):
# 	def __init__(self, p_thisnode, p_othernode, p_reltype: int):
# 		self.thisid = p_thisnode.ident
# 		self.otherid = p_othernode.ident
# 		self.reltype = p_reltype
# 	def __str__(self):
# 		if self.reltype == PARENT:
# 			ret = f"Node {self.otherid} already marked as parent of id: {self.thisid}"
# 		else:
# 			ret = f"Node {self.otherid} already marked as child of id: {self.thisid}"
# 		return ret

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

class SelfReferenceAttenpt(RuntimeError):
	def __init__(self, p_id):
		self.p_ids = p_id
	def __str__(self):
		return f"Attempt to self reference, id: {self.p_ids}"

class ImproperSortingMethod(RuntimeError):
	def __init__(self, p_classname):
		self.p_classname = p_classname
	def __str__(self):
		return f"Method __lt__ for sorting nodes is improperly extended for {self.p_classname}"
		
class BaseGraphNode(object):

	def __init__(self, ident: Optional[List[Union[str,int]]] = None, 
			parentids: Optional[List[Union[str,int]]] = None, 
			childrenids: Optional[List[Union[str,int]]] = None):
		if ident is None:
			self.ident = str(id(self))
		else:
			self.ident = ident
		if parentids is None:
			self.parentids = []
		else:
			self.parentids = parentids
		if childrenids is None:
			self.childrenids = []
		else:
			self.childrenids = parentids

	def __repr__(self):
		return str(self.ident)
		
	def __eq__(self, p_other):
		if not isinstance(p_other, BaseGraphNode):
			raise NotBaseNodeError()
		return self.ident == p_other.ident
		
	def __ne__(self, p_other):
		if not isinstance(p_other, BaseGraphNode):
			raise NotBaseNodeError()
		return self.ident != p_other.ident
		
	def __lt__(self, p_other):
		"""THIS METHOD SHUOLD BE EXTENDED BY SUBCLASSES, TO PROPER SORT NODES ALONG Graph"""
		if not isinstance(p_other, BaseGraphNode):
			raise NotBaseNodeError()
		return self.ident < p_other.ident

	def getParentIds(self) -> List[Union[str,int]]:
		return self.parentids

	def getChildrenIds(self) -> List[Union[str,int]]:
		return self.childrenids

	def removeParentId(self, p_pid: Union[str,int]):
		if p_pid in self.parentids:
			self.parentids.remove(p_pid)

	def removeChildId(self, p_cid: Union[str,int]):
		if p_cid in self.childrenids:
			self.childrenids.remove(p_cid)

	def assertOtherIsParent(self, p_other):
		if not isinstance(p_other, BaseGraphNode):
			raise NotBaseNodeError()
		if not p_other.ident in self.getParentIds():
			self.parentids.append(p_other.ident)
		if not self.ident in p_other.getChildrenIds():
			p_other.childrenids.append(self.ident)

	def assertOtherIsChild(self, p_other):
		if not isinstance(p_other, BaseGraphNode):
			raise NotBaseNodeError()
		if not p_other.ident in self.getChildrenIds():
			self.childrenids.append(p_other.ident)
		if not self.ident in p_other.getParentIds():
			p_other.parentids.append(self.ident)

	# def removeOtherFromChildren(self, p_other):
	# 	if not isinstance(p_other, BaseGraphNode):
	# 		raise NotBaseNodeError()
	# 	if p_other.ident in self.getChildrenIds():
	# 		self.childrenids.remove(p_other.ident)
	# 	if self.ident in p_other.getParentIds():
	# 		p_other.parentids.remove(self.ident)

	# def removeOtherFromParents(self, p_other):
	# 	if not isinstance(p_other, BaseGraphNode):
	# 		raise NotBaseNodeError()
	# 	if p_other.ident in self.getParentIds():
	# 		self.parentids.remove(p_other.ident)
	# 	if self.ident in p_other.getChildrenIds():
	# 		p_other.childrenids.remove(self.ident)

class DirectedAciclicGraph(object):	
	
	def __init__(self):
		self.rootids: List[Union[str,int]] = []		
		self.nodes = {}
		
	def checkIDs(self, lids: List[Union[str,int]]) -> None:
		if len(lids) < 1:
			return
		tstids = set(lids)
		xstkeys = set(self.nodes.keys())
		if len(xstkeys) > 0 and tstids.isdisjoint(xstkeys):
			raise MissingNodeIDsError(tstids.difference(xstkeys))	
			
	def iterateUp(self, start_ident: Optional[Union[str,int]] = None, 
			parentids: Optional[List[Union[str,int]]] = None) -> None:

		assert not start_ident is None or \
			not parentids is None
		
		if not start_ident is None and not start_ident in self.nodes.keys():
			raise MissingNodeIDsError(start_ident)
			
		fringe = PriorityQueue()
		fringed_ids = set()
		lvl = 0

		if not start_ident is None:
			
			n = self.nodes[start_ident]
			fringe.put((lvl, n))
			lvl += 1
		
			for pid in n.parentids:
				p = self.nodes[pid]
				fringe.put((lvl, p))
				fringed_ids.add(pid)

		else:

			for pid in parentids:
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

	def iterateDown(self, start_ident: Optional[Union[str,int]] = None, 
			childrenids: Optional[List[Union[str,int]]] = None) -> None:

		assert not start_ident is None or \
			not childrenids is None

		if not start_ident is None and not start_ident in self.nodes.keys():
			raise MissingNodeIDsError(start_ident)
			
		fringe = PriorityQueue()
		fringed_ids = set()
		lvl = 0

		if not start_ident is None:
			
			n = self.nodes[start_ident]
			fringe.put((lvl, n))
			lvl += 1
			
			for pid in n.childrenids:
				p = self.nodes[pid]
				fringe.put((lvl, p))
				fringed_ids.add(pid)

		else:

			for pid in childrenids:
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
		
	def addNode(self, p_node: BaseGraphNode, doraise: Optional[bool] = False) -> BaseGraphNode:	

		if not isinstance(p_node, BaseGraphNode):
			raise NotBaseNodeError()

		if p_node.ident in self.nodes.keys():
			raise ExistingNodeIdError(p_node.ident)

		chldids = set(p_node.getChildrenIds())
		parids = set(p_node.getParentIds())

		if p_node.ident in chldids or p_node.ident in parids:
			raise SelfReferenceAttenpt(p_node.ident)

		cycle_alarm_ids = set()
		# prevent cycles: upward
		iup = {n.ident for n in self.iterateUp(parentids = parids)}
		if len(chldids) > 0 and len(iup) > 0 and chldids.issubset(iup):
			for xcid in chldids.intersection(iup):
				cycle_alarm_ids.add(xcid)
				p_node.removeChildId(xcid)

		# prevent cycles: downward
		idn = {n.ident for n in self.iterateDown(childrenids=chldids)}
		if len(parids) > 0 and len(idn) > 0 and parids.issubset(idn):
			for xpid in parids.intersection(idn):
				cycle_alarm_ids.add(xpid)
				p_node.removeParentId(xpid)

		if doraise and len(cycle_alarm_ids) > 0:
			raise CycleAttemptError(cycle_alarm_ids)

		chldids = set(p_node.getChildrenIds())
		parids = set(p_node.getParentIds())

		self.checkIDs(parids)
		self.checkIDs(chldids)

		lparents = [self.nodes[pid] for pid in parids]
		lchildren = [self.nodes[cid] for cid in chldids]

		if len(lparents) > 0:
			for parnode in lparents:
				p_node.assertOtherIsParent(parnode)
		else:
			if len(chldids) > 0:
				roots_to_cancel = chldids.intersection(set(self.rootids))
				for rtc in roots_to_cancel:
					self.rootids.remove(rtc)
			self.rootids.append(p_node.ident)

		if len(lchildren) > 0:
			for chldnode in lchildren:
				p_node.assertOtherIsChild(chldnode)

		self.nodes[p_node.ident] = p_node
		
		return self.nodes[p_node.ident]

	def getNode(self, p_ident: str, doraise: Optional[bool] = False) -> Union[None, BaseGraphNode]:

		if p_ident is None or not p_ident in self.nodes.keys():
			if doraise:
				raise MissingNodeIDsError(p_ident)
			ret = None
		else:
			ret = self.nodes[p_ident]

		return ret

	def addEdge(self, p_fromid: Union[str,int], p_toid: Union[str,int], doraise: Optional[bool] = False) -> Union[None,BaseGraphNode]:

		ret = None

		if not p_fromid in self.nodes.keys():
			raise MissingNodeIDsError(p_fromid)
		if not p_toid in self.nodes.keys():
			raise MissingNodeIDsError(p_toid)

		if p_fromid == p_toid:
			raise SelfReferenceAttenpt(p_fromid)

		# prevent cycles: upward
		cycle_alarm_ids = set()
		for iid in self.iterateUp(start_ident=p_fromid):
			if p_toid == iid.ident:
				cycle_alarm_ids.add(p_toid)
				break

		for iid in self.iterateDown(start_ident=p_toid):
			if p_fromid == iid.ident:
				cycle_alarm_ids.add(p_fromid)
				break

		if len(cycle_alarm_ids) > 0:
			if doraise:
				raise CycleAttemptError(cycle_alarm_ids)
		else:
			fnd = self.nodes[p_fromid]
			tnd = self.nodes[p_toid]
			fnd.assertOtherIsChild(tnd)
			ret = fnd

		return ret
		
		

def main():
	print("-A---------------------------------------")
	m = DirectedAciclicGraph()
	m.addNode(BaseGraphNode(ident="zeroot"))
	m.addNode(BaseGraphNode(ident="zefilhoa", parentids=["zeroot"]))
	m.addNode(BaseGraphNode(ident="zefilhob", parentids=["zeroot"]))
	m.addNode(BaseGraphNode(ident="zenetob", parentids=["zefilhoa", "zefilhob"]))
	m.addNode(BaseGraphNode(ident="zbisenetob", parentids=["zenetob"]))
	m.addNode(BaseGraphNode(ident="zbisenetoc", parentids=["zenetob"]))
	print("Root ids:", m.rootids)
	print("Nodes:",m.nodes.keys())
	print("Iterate up zbisenetob:",  list(m.iterateUp("zbisenetob")))
	print("Iterate down zeroot:",list(m.iterateDown("zeroot")))
	print("-B---------------------------------------")
	for k, v in m.nodes.items():
		print(k , v.__dict__)
	print("-C---------------------------------------")
	m.addEdge("zeroot", "zenetob", doraise=True)
	for k, v in m.nodes.items():
		print(k , v.__dict__)
	print("Iterate up zbisenetob 2nd:",  list(m.iterateUp("zbisenetob")))
	print("-D---------------------------------------")
	m.addEdge("zenetob", "zeroot", doraise=True)



if __name__ == "__main__":
	main()

