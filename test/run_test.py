from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util

from test import testNode

wf = Workflow(name='test')
tt = testNode()

# subjects infosource
subjects_infosource = Node(util.IdentityInterface(fields=['subject_id']), name="subjects_infosource")
subjects_infosource.iterables = ('subject_id', [4])

wf.connect(subjects_infosource, "subject_id", tt, "inputnode.hpval")

wf.run()

