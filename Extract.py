from abaqus import *
from abaqusConstants import *
import displayGroupOdbToolset as dgo

# Open Odb file, show only footing instance and adjuct view point
#################################################
odbName='asd16_9_14d3pci'
output_nodes={'A':103, 'B':53, 'C':66, 'D':65, 'E':98, 'F':88, 'G':52, 'H':111}
ins_name='FOOTING-1'
#################################################
components=['U1','U2','U3']
o2 = session.openOdb(name=odbName+'.odb',readOnly=True)
session.viewports['Viewport: 1'].setValues(displayedObject=o2)
leaf = dgo.LeafFromPartInstance(partInstanceName=('FOOTING-1', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
session.graphicsOptions.setValues(backgroundColor='#FFFFFF')
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(title=OFF, state=OFF)
session.viewports['Viewport: 1'].view.rotate(xAngle=90, yAngle=-90, zAngle=0, mode=TOTAL)
session.viewports['Viewport: 1'].view.fitView()

#Add letters for corners
t = o2.userData.Text(name='A', text='A', offset=(264.126, 230.04), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='B', text='B', offset=(266.554, 132.03), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='C', text='C', offset=(312.689, 130.14), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='D', text='D', offset=(314.038, 5.94), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='E', text='E', offset=(70.1458, 8.1), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='F', text='F', offset=(68.7969, 130.41), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='G', text='G', offset=(132.738, 130.95), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='H', text='H', offset=(133.547, 231.66), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    legendDecimalPlaces=2, legendNumberFormat=FIXED)

#Generate sets for output nodes
nodes=[]
node_set_name=[]
for set_name, node in output_nodes.items():
#    if 'Output_'+set_name in o2.rootAssembly.instances[ins_name].nodeSets.keys():
    ss=o2.rootAssembly.instances[ins_name].NodeSetFromNodeLabels(name='Output_'+set_name, nodeLabels=(node,))
    node_set_name.append(ins_name+'.Output_'+set_name)
    nodes.append(ss)

#Get non-empty step number and frame number, save the last frame number in each step
step_item=o2.steps.items()
step_dic={}
for step_i, n in enumerate(step_item):
    step_name, odb_step=n
    if len(odb_step.frames)>0:
        step_dic[step_name]=[step_i,len(odb_step.frames)-1]

#Loop over steps and output figures and displacement
for uu in components:
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, uu), )
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_UNDEF, ))
    for step_name, frame_no in step_dic.items():
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=frame_no[0], frame=frame_no[1])
        session.printToFile(fileName=odbName+'_'+str(frame_no[0])+'_'+step_name+'_'+uu, format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))

print('Figuers Done')

leaf = dgo.LeafFromNodeSets(nodeSets=node_set_name)
session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
session.fieldReportOptions.setValues(printTotal=OFF, printMinMax=OFF)
for step_name, frame_no in step_dic.items():
    session.writeFieldReport(fileName=str(frame_no[0])+'_'+step_name+'.txt', append=OFF, 
            sortItem='Node Label', odb=o2, step=frame_no[0], frame=frame_no[1], outputPosition=NODAL, 
            variable=(('U', NODAL, ((COMPONENT, 'U1'), (COMPONENT, 'U2'), (COMPONENT, 'U3'), )), ))



nodes_sort=[[i,j] for i, j in output_nodes.items()]
nodes_sort.sort(key=lambda x:x[0])
step_sort=[[i,j] for i, j in step_dic.items()]
step_sort.sort(key=lambda x:x[1][0])

with open('Extracted_Displacement.txt','w') as f_out:
    f_out.write('\t')
    [f_out.write('{0}({1}) U1\t{0}({1}) U2\t{0}({1}) U3\t'.format(i,j)) for  i, j in nodes_sort]
    f_out.write('\n')
    for step_name, frame_no in step_sort:
        f_out.write(str(frame_no[0])+'_'+step_name+'\t')
        with open(str(frame_no[0])+'_'+step_name+'.txt','r') as f_inp:
            lines=f_inp.readlines()
            data=lines[19:-2]
            disp_data={}
            for line in data:
                keys=line.split()
                nn=int(keys[0])
                u1=float(keys[1])
                u2=float(keys[2])
                u3=float(keys[3])
                disp_data[nn]=[u1,u2,u3]
        [f_out.write('{0[0]}\t{0[1]}\t{0[2]}\t'.format(disp_data[j])) for i, j in nodes_sort]
        f_out.write('\n')

print('Discpalcement Done')

