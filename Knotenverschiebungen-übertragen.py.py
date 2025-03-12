from odbAccess import openOdb
from abaqus import *
from abaqusConstants import *
from regionToolset import Region
import csv

# 1. Angabe ODB-Pfad zur Auslesung der Knotenverschiebungen aus Simulationsergebnis
odb_path = 'G:/Meine Ablage/Masterarbeit/Abaqus Modelle/Rekonstruktion Sitzdruckverteilung/Zwischenstand_20241201/SDV_w5perzitil/Rekonstruktion-SDVw5perzitil.odb' 
odb = openOdb(path=odb_path)

step_name = "Step-1"
frame_number = -1  # Letzter Frame
displacement_output = odb.steps[step_name].frames[frame_number].fieldOutputs['U']

node_set_name = 'TOPSURF'
region = odb.rootAssembly.nodeSets[node_set_name]

# Verschiebungen in u1 (x-Richtung) für jeden Knoten im Node Set auslesen
u1_displacements_per_node = {}
for value in displacement_output.getSubset(region=region).values:
    node_id = value.nodeLabel
    u1_displacements_per_node[node_id] = -abs(value.data[0])
odb.close()

print("Verschiebungen in u1 (x-Richtung) mit negativen Vorzeichen:")
for node_id, u1_displacement in u1_displacements_per_node.items():
    print("Knoten {0}: u1 = {1:.6f}".format(node_id, u1_displacement))

# 2. Neues Modell erstellen (als Kopie von Model-1)
current_model_name = 'Model-1'
new_model_name = 'Model-3'
mdb.Model(name=new_model_name, objectToCopy=mdb.models[current_model_name])

instance_name = 'Schaumersatzstruktur-1'
model = mdb.models[new_model_name]

# Boundary Conditions für jeden Knoten im Node Set für Model-2 setzen
for node_id, u1_displacement in u1_displacements_per_node.items():
    model.DisplacementBC(
        name='BC_Node_{0}'.format(node_id),
        createStepName='Step-1',
        region=Region(
            nodes=model.rootAssembly.instances[instance_name].nodes[node_id-1:node_id]
        ),
        u1=u1_displacement, 
        u2=0, 
        u3=0,  
        amplitude=UNSET,
        distributionType=UNIFORM,
        fieldName='',
        localCsys=None
    )

print("Neues Modell '{0}' wurde erstellt und Boundary Conditions wurden definiert!".format(new_model_name))

# 3. Datei mit Knoten-ID und Verschiebung erstellen für ggf. weitere Analysen
output_path = r"G:/Meine Ablage/Masterarbeit/Abaqus Modelle/Rekonstruktion Sitzdruckverteilung/Zwischenstand_20241201/SDV_w5perzitil/Output-Displacement.csv"

with open(output_path, mode='w') as file:
    writer = csv.writer(file)
    writer.writerow(["Knoten ID", "Verschiebung in mm"])
    for node_id, u1_displacement in u1_displacements_per_node.items():
        writer.writerow([node_id, u1_displacement])

print("Tabelle wurde erstellt und gespeichert unter:", output_path)
