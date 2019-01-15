# Changed to multiple instances
from abaqus import *
from abaqusConstants import *
import displayGroupOdbToolset as dgo

# Open Odb file, show only footing instance and adjuct view point
#################################################
odbName='asd16_9_14d3pci'
output_nodes_list=[{'A':7308, 'B':7878, 'C':6306, 'D':6267},
        {'E':2934, 'F':3688}]
ins_name_list=['HIBAYROOF-1', 'LOWBAYROOF-1']
#################################################
components=['U1','U2','U3']
o2 = session.openOdb(name=odbName+'.odb',readOnly=True)
session.viewports['Viewport: 1'].setValues(displayedObject=o2)
leaf = dgo.LeafFromPartInstance(partInstanceName=ins_name_list)
session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
session.graphicsOptions.setValues(backgroundColor='#FFFFFF')
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(title=OFF, state=OFF)
session.viewports['Viewport: 1'].view.rotate(xAngle=90, yAngle=-90, zAngle=0, mode=TOTAL)
session.viewports['Viewport: 1'].view.fitView()

#Add letters for corners
t = o2.userData.Text(name='A', text='A', offset=(308.372, 124.2), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='B', text='B', offset=(309.181, 5.94), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='C', text='C', offset=(72.8438, 6.48), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='D', text='D', offset=(73.1135, 123.93), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='E', text='E', offset=(130.579, 235.44), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
t = o2.userData.Text(name='F', text='F', offset=(265.205, 235.98), backgroundStyle=MATCH)
session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
#t = o2.userData.Text(name='G', text='G', offset=(132.738, 130.95), backgroundStyle=MATCH)
#session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
#t = o2.userData.Text(name='H', text='H', offset=(133.547, 231.66), backgroundStyle=MATCH)
#session.viewports['Viewport: 1'].plotAnnotation(annotation=t)
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    legendDecimalPlaces=2, legendNumberFormat=FIXED)

#Generate sets for output nodes
nodes=[]
node_set_name=[]
for i, ins_name in enumerate(ins_name_list):
    for set_name, node in output_nodes_list[i].items():
        ss=o2.rootAssembly.instances[ins_name].NodeSetFromNodeLabels(name='Output_Roof'+set_name, nodeLabels=(node,))
        node_set_name.append(ins_name+'.Output_Roof'+set_name)
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
        session.printToFile(fileName=odbName+'_Roof_'+str(frame_no[0])+'_'+step_name+'_'+uu, format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))

print('Figuers Done')

leaf = dgo.LeafFromNodeSets(nodeSets=node_set_name)
session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
session.fieldReportOptions.setValues(printTotal=OFF, printMinMax=OFF)
for step_name, frame_no in step_dic.items():
    session.writeFieldReport(fileName=str(frame_no[0])+'_'+step_name+'.txt', append=OFF, 
            sortItem='Node Label', odb=o2, step=frame_no[0], frame=frame_no[1], outputPosition=NODAL, 
            variable=(('U', NODAL, ((COMPONENT, 'U1'), (COMPONENT, 'U2'), (COMPONENT, 'U3'), )), ))

nodes_sort=[]
for ii, output_nodes in enumerate(output_nodes_list):
    [nodes_sort.append([i,j,ins_name_list[ii]]) for i, j in output_nodes.items()]
nodes_sort.sort(key=lambda x:x[0])

step_sort=[[i,j] for i, j in step_dic.items()]
step_sort.sort(key=lambda x:x[1][0])

with open('Extracted_Displacement_Roof.txt','w') as f_out:
    f_out.write('\t')
    [f_out.write('{0}({2}.{1}) U1\t{0}({2}.{1}) U2\t{0}({2}.{1}) U3\t'.format(i,j,k)) for  i, j, k in nodes_sort]
    f_out.write('\n')
    for step_name, frame_no in step_sort:
        f_out.write(str(frame_no[0])+'_'+step_name+'\t')
        with open(str(frame_no[0])+'_'+step_name+'.txt','r') as f_inp:
            lines=f_inp.readlines()
            disp_data={}
            for i, line in enumerate(lines):
                if line=='\n':
                    continue
                if 'Field Output reported at nodes for part' in line:
                    current_ins=line[line.index(':')+2:-1]
                if line.strip()[0].isdigit():
                    keys=line.split()
                    nn=int(keys[0])
                    u1=float(keys[1])
                    u2=float(keys[2])
                    u3=float(keys[3])
                    disp_data[current_ins+'.'+str(nn)]=[u1,u2,u3]
        [f_out.write('{0[0]}\t{0[1]}\t{0[2]}\t'.format(disp_data[k+'.'+str(j)])) for i, j, k in nodes_sort]
        f_out.write('\n')

print('Discpalcement Done')

