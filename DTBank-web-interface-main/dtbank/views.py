from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.hashers as hasher
from django.shortcuts import redirect
from django.db import connection
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view


cursor = connection.cursor()

#
#   *** GENERAL
#

#redirects to login page
def home(request):
	return redirect('login')

#Renders user login page which requests username, institution and password of the user.
def userloginpage(request):
	return render(request, 'login.html')

#Renders database manager login page which requests username and password of the manager.
def managerloginpage(request):
	return render(request, 'managerlogin.html')

"""
Checks the info of user to login. Returns a message if there is no such user or password is incorrect.
Renders user homepage if the password is correct.
"""
def login(request):
	username = request.POST.get('username')	#check if username exists in database
	institution = request.POST.get('institution')
	password = request.POST.get('password')

	query = "select password from User_Work where username='"+username+"' and institution_name='"+institution+"'"
	cursor.execute(query)
	encodedtuple = cursor.fetchall()
	if len(encodedtuple)==0:
		return render(request, 'login.html', {'message': "Invalid username or password!"})

	encoded = encodedtuple[0][0]		#check if there is any value

	if hasher.check_password(password, encoded):	#check database user - password
		return render(request, 'userhome.html', {'username':username})
	else:
		return render(request, 'login.html', {'message': "Invalid username or password!"})

"""
Checks the info of db manager to login. Returns a message if there is no such manager or password is incorrect.
Renders manager homepage if the password is correct.
"""
def managerlogin(request):
	username = request.POST.get('username')	#check if username exists in database
	password = request.POST.get('password')
	#if hasher.check_password(password, encoded): #check database manager - password
	query = "select password from Database_Manager where username='"+username+"'"
	cursor.execute(query)
	encodedtuple = cursor.fetchall()
	if len(encodedtuple)==0:
		return render(request, 'managerlogin.html', {'message': "Invalid username or password!"})
		
	encoded = encodedtuple[0][0]		#check if there is any value

	if hasher.check_password(password, encoded):
		return render(request, 'managerhome.html', {'message':'Welcome '+username+"!"})
	else:
		return render(request, 'managerlogin.html', {'message': "Invalid username or password!"})

"""
Renders user homepage.
This function is used facilitate already logged in user to return to homepage.
"""
def userhome(request, username):
	return render(request, 'userhome.html')

"""
Renders database manager homepage.
This function is used facilitate already logged in database manager to return to homepage.
"""
def managerhome(request):
	return render(request, 'managerhome.html')
	
#
#	*** User Operations
#
""" Requirements 8:  We selected all values related with this requirement from tables then render these values to viewtable. 

"""


def viewDrugInfo(request):
	cursor.execute("select drugbank_id, drug_name, smiles, description from Drug")
	drugs = cursor.fetchall()

	cursor.execute("select D.drugbank_id, D.drug_name,D.smiles, D.description, U.target_name  from Drug D, Reaction_Related R, UniProt U where D.drugbank_id=R.drugbank_id and R.uniprot_id=U.uniprot_id")
	targets = cursor.fetchall()
	cursor.execute("select D.drugbank_id, D.drug_name,D.smiles, D.description, S.side_effect_name  from Drug D, Sider_Has S where D.drugbank_id=S.drugbank_id")
	sides = cursor.fetchall()
	
	columns = ["Drugbank ID", "Drug Name", "Smiles", "Description", "Target Name", "Side Effect Name"]

	dct = {drug:[[],[]] for drug in drugs}

	for tpl in targets:
		dct[(tpl[0],tpl[1], tpl[2], tpl[3])][0].append(tpl[4])

	for tpl in sides:
		dct[(tpl[0],tpl[1], tpl[2], tpl[3])][1].append(tpl[4])

	tuples = [(k[0],k[1], k[2], k[3], v[0], v[1]) for k,v in dct.items()]

	return render(request, "viewtable.html", {'tuples':tuples, 'columns':columns})
""" Requirements 9: User enter a drugbank_id and we select all drugs from interaction_with table. Than we select names of these drugs
	from the Drug table. We check if the given id is valid or not. If it is valid render the values to viewtable

"""

def viewdruginteractions(request):
	drugbank_id = request.POST.get('id')
	cursor.execute("select drugbank_id_2 from Interaction_with where drugbank_id_1 = '"+drugbank_id+"'")
	ts = cursor.fetchall()
	interactions = [t[0] for t in ts]
	names = []
	for drug in interactions:
		cursor.execute("select drug_name from Drug where drugbank_id='"+drug+"'")
		names.append(cursor.fetchall()[0])
	names = [name[0] for name in names]

	tuples = []
	for i in range(len(interactions)):
		tuples.append((interactions[i],names[i]))
	
	cursor.execute("select drugbank_id from Drug")
	drugs1 = [i[0] for i in cursor.fetchall()]
	if drugbank_id not in drugs1:
		return render(request,'viewtable.html', {'message':"There is no such drug. Please try again!"})
	
	else:

		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Drug id", "Drug name"]})

"""User enters a drugbank_id and we select all side effect names and umls_cui from table and render these value to 
view table.

"""
def viewSideEffects(request):
	drugbank_id = request.POST.get('id')
	cursor.execute("select side_effect_name, umls_cui from Sider_Has where drugbank_id = '"+drugbank_id+"'")
	tuples = cursor.fetchall()
	cursor.execute("select drugbank_id from Drug") # all drugs
	drugs1 = [i[0] for i in cursor.fetchall()]
	if drugbank_id not in drugs1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such drug. Please try again!"})
	
	else:
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Side Effect Name", "UMLS CUI"]} )

""" User enters a drugbank_id and we select all proteins and their names from tables and render these values to view table.


"""
def viewdruginteractingtargets(request):
	drugbank_id = request.POST.get('id')
	cursor.execute("select uniprot_id from Reaction_Related where drugbank_id = '"+drugbank_id+"' ")
	ts = cursor.fetchall()
	interacting=[t[0] for t in ts]
	names=[]
	for prot in interacting:
		cursor.execute("select target_name from Uniprot where uniprot_id='"+prot+"'")
		names.append(cursor.fetchall()[0])
	names = [name[0] for name in names]
	tuples = []
	for i in range(len(interacting)):
		tuples.append((interacting[i],names[i]))
	cursor.execute("select drugbank_id from Drug") # all drugs
	drugs1 = [i[0] for i in cursor.fetchall()]
	if drugbank_id not in drugs1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such drug. Please try again!"})
	else:	
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Uniprot ID","Target Name"]} )

""" Unser enters a protein and we select all drugs interacting with this protein and their names from table and render it to view table
"""
def viewproteininteractings(request):
	uniprot_id = request.POST.get('id')
	cursor.execute("select drugbank_id  from Reaction_Related where uniprot_id = '"+uniprot_id+"'")
	ts = cursor.fetchall()
	interacting=[t[0] for t in ts]
	names=[]
	for drug in interacting:
		cursor.execute("select drug_name from Drug where drugbank_id='"+drug+"'")
		names.append(cursor.fetchall()[0])
	names = [name[0] for name in names]

	tuples = []
	for i in range(len(interacting)):
		tuples.append((interacting[i],names[i]))
	cursor.execute("select uniprot_id from Uniprot") # all proteins
	prots1 = [i[0] for i in cursor.fetchall()]
	if uniprot_id not in prots1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such Protein. Please try again!"})
	else:	
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Interacting Drugs", "Drug Name"]} )


""" firts we select all proteins from table. Then we select drugs interacitong with same protein. Then assigne these drugs as dictionary value and 
realated proteins as dictionary keys. Then render these values to view table.
"""	
def sameproteindrugs(request):
	cursor.execute("select uniprot_id from Uniprot")
	prots= cursor.fetchall()
	keys = []
	for prot in prots:
		keys.append(prot[0])
	dct = {key:[] for key in keys}

	cursor.execute("select distinct(R1.drugbank_id), R1.uniprot_id from Reaction_Related R1, Reaction_Related R2  where R1.uniprot_id = R2.uniprot_id")
	tuples = cursor.fetchall()
	
	for tpl in tuples:
		
		dct[tpl[1]].append(tpl[0])

	tuples = [(k,v) for k,v in dct.items()]
	columns = ["Uniprot ID","Drugs That Affect"]
	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})
"""
We did same procedure with above funciton for drugs
"""

def samedrugproteins(request):
	cursor.execute("select drugbank_id from Drug")
	drugs= cursor.fetchall()
	keys = []
	for drug in drugs:
		keys.append(drug[0])
	dct = {key:[] for key in keys}

	cursor.execute("select distinct(R1.uniprot_id), R1.drugbank_id from Reaction_Related R1, Reaction_Related R2  where R1.drugbank_id = R2.drugbank_id")
	tuples = cursor.fetchall()
	
	for tpl in tuples:
		
		dct[tpl[1]].append(tpl[0])

	tuples = [(k,v) for k,v in dct.items()]
	columns = ["DrugBank ID","Proteins That Bind"]
	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})	

"""User enters a sider and we select all drugs that has this sider and their names. Then render them to view table

"""
def viewdrugswithsider(request):
	umls_cui = request.POST.get('id')
	cursor.execute("select S.drugbank_id, D.drug_name from Sider_Has S, Drug D where umls_cui = '"+umls_cui+"' and S.drugbank_id=D.drugbank_id ")
	tuples = cursor.fetchall()
	cursor.execute("select umls_cui from Sider_Has") # all siders
	sider1 = [i[0] for i in cursor.fetchall()]
	if umls_cui not in sider1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such side effect. Please try again!"})
	else:	
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["DrugBank ID", "Drug Name"]} )

"""
User enters a keyword and we select drugs that includes these keywords in their discriptions. Then render them to view table
"""

def searchandviewdrugs(request):
	keyword = request.POST.get('id')
	cursor.execute("select drugbank_id, drug_name, description from Drug where description like CONCAT('%', '"+keyword+"', '%');")
	tuples = cursor.fetchall()
	
	return render(request,"viewtable.html", {'tuples':tuples, 'columns':["DrugBank ID", "Drug Name", "Description"]} )	

"We select institutions order them by score in descending order"		

def rankinstitutes(request):
	cursor.execute("select institution_name, score from Institution order by score desc")
	tuples= cursor.fetchall()
	
	columns = ["Institute","Score"]
	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})

""" User enters a proteins then we select the drugs interacting with this protein and their count of side affects.
	Then we order these values count of side effects in ascending order. Then we check is there a drug with count value equals to first drug
	because the first one has least sider. Then find thse drugs' names and render them to view table.
"""
def viewdrugsleastside(request):
	uniprot_id = request.POST.get('id')
	cursor.execute("select R.drugbank_id, count(S.umls_cui) from Reaction_Related R , Sider_Has S where R.uniprot_id = '"+uniprot_id+"'and R.drugbank_id =S.drugbank_id  group by S.drugbank_id order by count(S.umls_cui) asc")
	ts = cursor.fetchall()
	interacting=[]
	for i in range(len(ts)):
		
		if(ts[i][1]==ts[0][1]):
			interacting.append(ts[i][0])
		else:
			break	


	names=[]
	for drug in interacting:
		cursor.execute("select drug_name from Drug where drugbank_id='"+drug+"'")
		names.append(cursor.fetchall()[0])
	names = [name[0] for name in names]

	tuples = []
	for i in range(len(interacting)):
		tuples.append((interacting[i],names[i]))
	
	cursor.execute("select uniprot_id from Uniprot") # all proteins
	prots1 = [i[0] for i in cursor.fetchall()]
	if uniprot_id not in prots1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such Protein. Please try again!"})
	else:	
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Interacting Drugs", "Drug Name"]} )


"""
We have a stored procedure with 3 paramaters that finds all drugs with these restrictions and their interacting proteins.
Then we just select wanted drugs amoung these drugs and find their interacting target name. Then we render them to view.  
"""
def filterdruginteractingtargets(request):
	
	drugbank_id = request.POST.get('id')
	type = request.POST.get('type')
	min = request.POST.get('min')
	max = request.POST.get('max')
	cursor.execute("CALL StoredProcedure('"+type+"',"+min+", "+max+" ) ")
	ts = cursor.fetchall()
	#interacting=[t[0] for t in ts]
	interacting=[]
	for t in ts:
		if(t[0]==drugbank_id):
			interacting.append(t[1])

	names=[]
	for prot in interacting:
		cursor.execute("select target_name from Uniprot where uniprot_id='"+prot+"'")
		names.append(cursor.fetchall()[0])
	names = [name[0] for name in names]
	tuples = []
	for i in range(len(interacting)):
		tuples.append((interacting[i],names[i]))
	
	cursor.execute("select drugbank_id from Drug") # all drugs
	drugs1 = [i[0] for i in cursor.fetchall()]
	cursor.execute("select measure from Reaction_Related") # all 
	meas = [i[0] for i in cursor.fetchall()] 

	if drugbank_id not in drugs1:  # If the input id is not from our database
		return render(request,'viewtable.html', {'message':"There is no such drug. Please try again!"})
	
	elif type not in meas:
		return render(request,'viewtable.html', {'message':"There is no such measurement type. Please try again!"})



	else:
		return render(request,"viewtable.html", {'tuples':tuples, 'columns':["Uniprot ID","Target Name"]} )


#
#	*** Database Manager operations
#

"""
Adds a new user to database with POST method. First checks if the institution exists or user already exists.
Encrypts the password and saves to database.
"""
def saveuser(request):
	username = request.POST.get('username')
	name = request.POST.get('name')
	institution = request.POST.get('institution')
	password = request.POST.get('password')
	cursor.execute("select institution_name from Institution")
	institutions = [i[0] for i in cursor.fetchall()]
	cursor.execute("select username, institution_name from User_Work")
	tuples = cursor.fetchall()
	if (username, institution) in tuples:
		return render(request,'managerhome.html', {'message':"User already exists!"})		#if user already exists
	elif institution not in institutions:
		return render(request,'managerhome.html', {'message':"There is no such institution. Please try again!"})	#if institution not exists return an error message
	else:
		encoded = hasher.make_password(password, hasher='pbkdf2_sha256')		#else save the username, institution name and the encrypted to database
		cursor.execute("insert into User_Work values ('"+username+"','"+name+"','"+institution+"','"+encoded+"')")
		return render(request,'managerhome.html', {'message':"User saved successfully!"})


#Updates affinity value of the given reaction id. First checks if the reaction with the given id exists.
def update_affinity(request):
	reaction_id = request.POST.get('id')
	newvalue = request.POST.get('affinity')
	cursor.execute("select * from Reaction_Related where reaction_id='"+reaction_id+"'")		#check if reaction exists
	temp = cursor.fetchall()
	if len(temp)==0:
		return render(request, 'managerhome.html',{'message':"There is no reaction with the given reaction id. Please try again."})
	else:
		update = "update Reaction_Related set affinity_NM= '"+newvalue+"' where reaction_id= '"+reaction_id+"'"		#if exists updates the affinity value
		cursor.execute(update)
		return render(request,'managerhome.html', {'message':"Affinity value updated successfully!"})

#Deletes the drug with the given id. First checks if there is a drug with the given id.
def delete_drug(request):
	drugbank_id = request.POST.get('id')
	cursor.execute("select * from Drug where drugbank_id= '"+drugbank_id+"'")		#check if drug exists
	temp = cursor.fetchall()
	if len(temp)==0:
		return render(request, 'managerhome.html', {'message':"There is no drug with the given id. Please try again."})
	else:
		deletion = "delete from Drug where drugbank_id= '"+drugbank_id+"'"			#if exists delete
		cursor.execute(deletion)
		return render(request,'managerhome.html', {'message':"Drug deleted successfully!"})

#Deletes the protein with the given id. First checks if there is a protein with the given id.
def delete_protein(request):
	uniprot_id = request.POST.get('id')
	cursor.execute("select * from UniProt where uniprot_id= '"+uniprot_id+"'")
	temp = cursor.fetchall()
	if len(temp)==0:
		return render(request, 'managerhome.html', {'message':"There is no protein with the given id. Please try again."})
	else:
		deletion = "delete from UniProt where uniprot_id= '"+uniprot_id+"'"
		cursor.execute(deletion)
		return render(request,'managerhome.html', {'message':"Protein deleted successfully!"})

# Takes tablename as parameter. Fetches its columns and entries. Sends to view table html file.
def viewtable(request, tablename):
	query = "select * from "+tablename
	cursor.execute(query)
	tuples = cursor.fetchall()
	cursor.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'dtbank' and TABLE_NAME= N'"+tablename+"'")
	columns = cursor.fetchall()
	columns = [col for (col,) in columns]
	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})

#Fetching entries in User_Work table without passwords sends to view table html file.
def viewusers(request):	
	cursor.execute("select name, username, institution_name from User_Work")
	tuples = cursor.fetchall()
	columns = ["name", "username", "institution"]		#arrrange column names
	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})

#Joining 3 tables, gets the doi, institution, authors. Sends to viewtable html to view papers.
def viewpapers(request):
	cursor.execute("select T1.doi, T3.name from Article_Institution T1, Article_Author T2, User_Work T3 where T1.doi = T2.doi and T2.username=T3.username and T1.institution_name=T3.institution_name")
	tuples = cursor.fetchall()
	columns = ["doi", "authors"]
	articles = []
	for tpl in tuples:								#create a dict whichs keys are articles
		if tpl[0] not in articles:
			articles.append(tpl[0])

	dct = {article:[] for article in articles}		#value of each key is empty list

	for tpl in tuples:								#add each author to its article list
		dct[tpl[0]].append(tpl[1])

	tuples = [(k,v) for k,v in dct.items()]			#convert dict to tuple

	return render(request, 'viewtable.html', {'tuples':tuples, 'columns': columns})

# Checks the given reaction id, returns a page with author info of the reaction.
def updateContributors(request):
	reaction_id = request.POST.get("reaction_id")
	cursor.execute("select doi from Reaction_Related where reaction_id= '"+reaction_id+"'")
	doi = cursor.fetchall()
	if len(doi)==0:
		return render(request, 'managerhome.html', {'message':"There is no reaction with the given id. Please try again."})
	else:
		doi=doi[0][0]
		cursor.execute("select username from Article_Author where doi='"+doi+"'")
		authors = cursor.fetchall()
		cursor.execute("select institution_name from Article_Institution where doi='"+doi+"'")
		institution = cursor.fetchall()[0][0]
		return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution})

# To add a new user as author, first saves it to User_Work table. Then saves to Article_Author to add as author of the article of given reaction.
def addauthors(request, reaction_id):
	username = request.POST.get('username')
	name = request.POST.get('name')
	cursor.execute("select doi from Reaction_Related where reaction_id='"+reaction_id+"'")		#get doi of the reaction
	doi = cursor.fetchall()[0][0]
	cursor.execute("select institution_name from Article_Institution where doi='"+doi+"'")		#get institution of the doi
	institution = cursor.fetchall()[0][0]
	institution = institution()
	password = request.POST.get('password')
	encoded = hasher.make_password(password, hasher='pbkdf2_sha256')		#save the username, institution name and the encrypted to database 
	cursor.execute("insert into User_Work values ('"+username+"','"+name+"','"+institution+"','"+encoded+"')")
	cursor.execute("insert into Article_Author values ('"+doi+"','"+username+"')")		#save as author
	cursor.execute("select username from Article_Author where doi='"+doi+"'")			#update the authors in the html page
	authors = cursor.fetchall()
	return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution, 'message':"Author added successfully!"})

# Adds user as author that already exists in the database. First checks if user exists in database.
def addUserAsAuthor(request, reaction_id):
	username = request.POST.get('username')
	cursor.execute("select doi from Reaction_Related where reaction_id='"+reaction_id+"'")
	doi = cursor.fetchall()[0][0]
	cursor.execute("select institution_name from Article_Institution where doi='"+doi+"'")
	institution = cursor.fetchall()[0][0]

	cursor.execute("select username from Article_Author where doi='"+doi+"'")
	authors = cursor.fetchall()

	cursor.execute("select * from User_Work where institution_name='"+institution+"' and username='"+username+"'")
	check = cursor.fetchall()

	if len(check)>0:			#check if user exists in the database
		insertion = "insert into Article_Author values ('"+doi+"','"+username+"')"
		cursor.execute(insertion)
		cursor.execute("select username from Article_Author where doi='"+doi+"'")
		authors = cursor.fetchall()
		return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution, 'message':"Author added successfully!"})
	else:
		return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution, 'message':"There is no such user. Please add as a new user."})

#removes author with the given username from article with the given reaction id
def removeauthor(request, username, reaction_id):
	cursor.execute("select doi from Reaction_Related where reaction_id='"+reaction_id+"'")
	doi = cursor.fetchall()[0][0]
	cursor.execute("select username from Article_Author where doi='"+doi+"'")
	authors = cursor.fetchall()
	cursor.execute("select institution_name from Article_Institution where doi='"+doi+"'")
	institution = cursor.fetchall()[0][0]

	if len(authors)<=1:
		return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution, 'message':"There should be at least 1 author!"})
	else:
		delete = "delete from Article_Author where username= '"+username+"' and doi='"+doi+"'"
		cursor.execute(delete)
		cursor.execute("select username from Article_Author where doi='"+doi+"'")
		authors = cursor.fetchall()
		return render(request, 'updatecontributors.html', {'reaction_id':reaction_id, 'doi':doi, 'authors':authors, 'institution':institution, 'message':"Author removed successfully!"})

"""
path: "encrypt/"
It is executed after loading data into databse. It encrypts the passwords in the database. It should not be executed in the later steps to not encrypt twice.
Passwords of users added by database managers are encrypted in their own function.
"""
def encrypt_passwords(request):
			#encode database manager passwords
	cursor.execute("select username, password from Database_Manager")
	user_password = cursor.fetchall()

	for username, password in user_password:
		encoded = hasher.make_password(password)
		query = "update Database_Manager set password='"+encoded+"' where username='"+username+"'"
		cursor.execute(query)

	cursor.execute("select username, institution_name, password from User_Work")	#encode user passwords
	user_password = cursor.fetchall()

	for username, institution, password in user_password:
		encoded = hasher.make_password(password)
		query = "update User_Work set password='"+encoded+"' where username='"+username+"' and institution_name= '"+institution+"'"
		cursor.execute(query)

	return redirect('login')

