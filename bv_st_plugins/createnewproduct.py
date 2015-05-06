import sublime, sublime_plugin, os
from ftplib import FTP
from random import randint
import http.client
import urllib.parse

# This class gathers all user inputs and passes them to the next function
class promptcreatenewproductCommand(sublime_plugin.WindowCommand):
	def run(self):

		self.window.show_input_panel("Create New Product| Enter ProductID:","Product1",self.pid_done,None,None)

	def pid_done(self, data):
		self.pid = data
		self.get_clientname()

	def get_clientname(self):
		self.window.show_input_panel("Create New Product| Enter Client:","smb-demo",self.clientname_done,None,None)

	def clientname_done(self, data):
		self.clientname = data
		self.get_imageURL()

	def get_imageURL(self):
		self.window.show_input_panel("Create New Product| Enter Image URL:","http://placehold.it/500X500",self.imageURL_done,None,None)

	def imageURL_done(self, data):
		self.imageURL = data
		self.get_pname()

	def get_pname(self):
		self.window.show_input_panel("Create New Product| Enter Product Name (Company if Finserv):","Red Stapler",self.pname_done,None,None)

	def pname_done(self, data):
		self.pname = data
		self.get_ptype()

	def get_ptype(self):
		self.window.show_input_panel("Review Template (Electronics[1], Health & Beauty[2], Finserv[3], Apparel[4], Outdoors[5]","1",self.ptype_done,None,None)

	def ptype_done(self, data):
		self.ptype = data
		self.cnp_continue()
		
	def cnp_continue(self):
		self.window.run_command("createfile",{ "clientname": self.clientname, "externalid": self.pid, "productname": self.pname, "imageurl": self.imageURL, "ptype": self.ptype} )

# This class is responible for creating and uploading the product feed
class createfileCommand(sublime_plugin.WindowCommand):
	def run(self, clientname, externalid, productname, imageurl, ptype):
		
		# Product Feed Template
		templatexml = '<?xml version="1.0" encoding="UTF-8"?><Feed xmlns="http://www.bazaarvoice.com/xs/PRR/ProductFeed/5.6" name="$CLIENTNAME$" incremental="true" extractDate="$DATE$"><Brands><Brand><ExternalId>brand1</ExternalId><Name>Brand</Name></Brand></Brands><Categories><Category><ExternalId>1</ExternalId><Name>Electronics</Name><CategoryPageUrl>http://brandbox.droppages.com/Products</CategoryPageUrl></Category></Categories><Products><Product><ExternalId>$EXTERNALID$</ExternalId><BrandExternalId>brand1</BrandExternalId><CategoryExternalId>1</CategoryExternalId><Name>$PRODUCTNAME$</Name><Description>Example Description</Description><ProductPageUrl>http://example.com/product1</ProductPageUrl><ImageUrl>$IMAGEURL$</ImageUrl></Product></Products></Feed>'

		# Text replacement in template
		templatexml = templatexml.replace("$DATE$", '2013-01-01T12:00:00.000000')
		templatexml = templatexml.replace("$CLIENTNAME$",clientname)
		templatexml = templatexml.replace("$EXTERNALID$",externalid)
		templatexml = templatexml.replace("$PRODUCTNAME$",productname)
		templatexml = templatexml.replace("$IMAGEURL$",imageurl)

		# Write feed to file with unique name and save
		filename = "bvintegratorproductfeed"+str(randint(0,999999))+".xml" 
		f = open(filename,"w+")
		f.write(templatexml)
		f.close()

		# Determine FTP credentials
		if clientname == 'smb-demo':
			passw = 'aVGe8&wG138K'
		elif clientname == 'sales-test':
			passw = 'lr3UptrqCp*N'
		else:
			# Fail out if FTP creds not avialable
			output = self.window.create_output_panel("error")
			output.run_command('append', {'characters': "Invalid clientname. Please use smb-demo or sales-test. Terminating...."})
			self.window.run_command("show_panel", {"panel": "output.error"})
			return

		# Connect to FTP and deliver Feed
		ftp = FTP(host='ftp-stg.bazaarvoice.com')
		ftp.login(clientname,passw)
		ftp.cwd('import-inbox')
		ftp.storlines("STOR " + filename, open(filename,"rb"))
		f.close()

		# pass inputs to and run content submitter
		self.window.run_command("submitreviews",{ "clientname": clientname, "externalid": externalid, "productname": productname, "imageurl": imageurl, "ptype": ptype} )

# This class is responsible for submitting the reviews through the API
class submitreviewsCommand(sublime_plugin.WindowCommand):
	def run(self, clientname, externalid, productname, imageurl, ptype):

		# Create output window for feedback
		output = self.window.create_output_panel("panelN")

		# Review templates for each supported category
		electronicsReviews = [["Great features and very versatile","I have used the "+productname+" for a few weeks now and I am very happy indeed with the quality and functionality of it.","johnny"+str(randint(0,9999))],["Awesome Product","I've had my "+productname+" for a week and its absolutely perfect! Although a steep price, I feel confident in its contruction and its easy to use. The battery life is spectacular. I use it for about 4 hours a day and its still has a great charge. The various modes make it incredibly versatile and I could not be happier. It takes a little getting used to with hand placement, but after a couple of days, I find it very easy to use. One other note, I would advise anyone to get one! Great product; intuitive and perfect.","nicki"+str(randint(0,9999))],["Aboslutely incredible","Ive had the "+productname+"  for over 4 months now and it is amazing. Its extremely versatile with multiple positions, using it is comfortable, the many light selections you can choose for the backlit keys is really fancy, and it is in fact quite rugged.  Everyone who sees the "+productname+" wants one, I got three other people from my class to get one! I highly recommend this product, it offers everything one needs from and provides so much more than the many other manufacturers can offer.","mario"+str(randint(0,9999))]]

		healthbeautyReviews = [["Look your best feel Amazing!","This product is amazing, everyone wants to be at the best and feel amazing without the irritating discoloration ok there face, not only with this product relieve with everyday facial occurrence but it will aheare to your makeup and leave amazing results.","Marsha"+str(randint(0,9999))],["My favorite of all time!","I received a deluxe sample of "+productname+" from one of my friends, and it is hands down, the best I've ever used. And as a beauty blogger, and as someone who worked in cosmetocs for almost 10 years, I've tried a ton. I have oily, acne prone skin, with visible pores. This product made my pores near-invisible, controlled oil, reduced my redness, and best of all - I didn't get ONE breakout while using. I featured this in one of my posts as well. Great job with this one! Can't wait to try out the rest of the brand!!","nicki"+str(randint(0,9999))],["A Must!","I tried "+productname+" for the first time a few years ago and there isn't a day I personally go without it ever since. It sets makeup in place extremely well for oily skin. For those who have more normal or more mature skin, I would recommend the illuminating setting powder which will still give some minor oil control but not give an overly matte appearance or set into any wrinkles. However, for those who are oily or tend to get oily throughout the day, you will not be disappointed with this product! Love love love!","linda"+str(randint(0,9999))]]

		finservReviews = [["Approved!!!","I couldn't be any more happy on how fast it was to get approved on a loan. I'm so glad I have been with "+productname+" with their unbeatable rates! God bless everyone that is part of the team.","Randy"+str(randint(0,9999))],["Approved for 30K 2.9% with Sub-Par Credit","Since they already pulled my credit for opening a CC, I inquired about a loan and was approved for $30K at 2.9%% despite a sub-700 credit score. I didn't take the loan since I still have student loan debt, but compared to my buddies interest rates, this seemed to be a pretty dang good offer.","Mark"+str(randint(0,9999))],["Excellent Service","I had a great experience with "+productname+" They're awesome! I have two loans with them. On my first car loan I had so much trouble getting financed through the dealer. The dealership was over charging me a car that was supposed to be $6000 came out to be $12325. I went to "+productname+" and I applied to a car the total came out to $9000 with "+productname+" that's including warranty and gap. Same thing happened with the car I just purchased a month ago. "+productname+" will save you money. My payments are so low. Also the service is fantastic all the employees here are so polite and helpful. I recommend "+productname+" to everyone!!!","Rachel"+str(randint(0,9999))]]

		apparelReviews = [["Great Item!!!","I love this style. This "+productname+" is great. I find a lot of variation in the sizes. Sometimes I go medium regular, sometimes large. It runs small so I don't get the petites, which I usually wear.","Mary"+str(randint(0,9999))],["Perfect","I love this "+productname+" ! I bought a size small at first, since I generally take small in clothes. However, the seams hit too high, it was too short, and the sleeves were a little too tight around me. I swapped it for a medium. The medium is perfect, especially since I like to wear my cardis buttoned up. For reference, I am 5'8\", 34A, 130, long-waisted. They are a touch loose around the bust, but not so loose that it's a problem. I have the black geo print and the color blocked gray version (with the floral now on the way, too!). I've washed both, and they came out looking like new (front loader, gentle cycle cold, air fluff to dry). Now I want one in every color :-)","Jeanie"+str(randint(0,9999))],["A staple in any wardrobe","I am really happy with this"+productname+" It is a nice, comfy staple. Quality is good and I am going to order it in another color. Fit is true to size. I am 5'4\", 127lbs and a size small fits perfect.","Rachel"+str(randint(0,9999))]]

		outdoorReviews = [["The Best!","I bought this bad boy about a month ago and it has stood up well to the desert. Now we use it in our home it's so convenient and useful. I'm very glad that I made this purchase.","Erin"+str(randint(0,9999))],["This is all I need.","Take this with me every where I go. looking to get another "+productname+" next. Won't use anything else. Works great with my tent, hat, koozie, and other camping equipment. Wether I'm trying to hunt, fish, camp, or hike, I always take my "+productname+". I talked several fellow Soldiers and family members to purchase them as well.","Jason"+str(randint(0,9999))],["Great!","I bought this for my charter boat, my clients are always amazed at how well it works, and how little trouble we have with it. "+productname+" is a must for a all day charter.","Nicholas"+str(randint(0,9999))]]

		# Determine product type based on input
		if ptype == '1' or ptype == 'Electronics' or ptype == 'electronics':
			reviews = electronicsReviews
		elif ptype == '2' or ptype == 'Health & Beauty' or ptype == 'health & beauty':
			reviews = healthbeautyReviews
		elif ptype == '3' or ptype == 'Finserv' or ptype == 'finserv':
			reviews = finservReviews
		elif ptype == '4' or ptype == 'Apparel' or ptype == 'apparel':
			reviews = apparelReviews
		elif ptype == '5' or ptype == 'Outdoors' or ptype == 'outdoors':
			reviews = outdoorReviews
		else:
			# Fail out if product type cannot be determined
			output = self.window.create_output_panel("error")
			output.run_command('append', {'characters': "Unable to determine Product Type. Please select from the list using numbers or words. Terminating..."})
			self.window.run_command("show_panel", {"panel": "output.error"})
			return

		#General Info output to user about what is happening
		output.run_command('append', {'characters': "Submitting review content on product "+ str(productname)+" ("+str(externalid)+ ") for " +str(clientname)+ ":\n"})

		# count for output
		count = 1

		# Define passkey based on clientname
		if clientname == 'smb-demo':
			apipasskey = 's5pfp4r4tgdurx257axt9z3a'
		elif clientname == 'sales-test':
			apipasskey = 'mpefzrxhjh3scwukynzqx73y'

		# Loop submits review based on templates
		for x in reviews:
			params = urllib.parse.urlencode({
				'ApiVersion' : '5.4',
				'ProductId' : externalid,
				'Action' : 'Submit',
				'Rating' : '5',
				'ReviewText' : x[1],
				'Title' : x[0],
				'UserNickname' : x[2],
				'PassKey' : apipasskey
    		})

			headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
			connection = http.client.HTTPConnection("stg.api.bazaarvoice.com:80")
			connection.request("POST", "/data/submitreview.json", params, headers)
			response = connection.getresponse()
			print (response.status, response.reason)
			connection.close()
			output.run_command('append', {'characters': "Review "+str(count)+": " + str(response.status) + " " + str(response.reason) + "\n"})
			count+=1

		# Show status
		self.window.run_command("show_panel", {"panel": "output.panelN"})

