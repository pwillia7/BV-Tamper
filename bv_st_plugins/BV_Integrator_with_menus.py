import sublime, sublime_plugin


class promptbazaarintegrateCommand(sublime_plugin.WindowCommand):
	def run(self):
		
		self.window.show_input_panel("ProductID:","Product1",self.pid_done,None,None)

	def get_client(self):
		self.window.show_input_panel("Client:","smb-demo",self.client_done,None,None)

	def get_dzone(self):
		self.window.show_input_panel("Deployment Zone:","Main%20Site",self.dzone_done,None,None)

	def client_done(self, data):
		self.client = data
		self.get_dzone()

	def pid_done(self, data):
		self.pid = data
		self.get_client()
	def dzone_done(self,data):
		self.dzone = data
		self.bvi_continue()
		
		
	def bvi_continue(self):
		self.window.run_command("bazaarintegrate", {"pid": self.pid, "client": self.client, "dzone": self.dzone} )

class bazaarintegrateCommand(sublime_plugin.TextCommand):
	def run(self, edit, pid, client, dzone):

		# -------------------------------------------- #
		fSource = '//display-stg.ugc.bazaarvoice.com/static/'+client+'/'+dzone+'/en_US/bvapi.js'
		productid = pid
		# -------------------------------------------- #


		region = sublime.Region(0, self.view.size())

		bvapijs = '<script type="text/javascript" Src="'+fSource+'"></script></head>'
		bvui = '<script type="text/javascript">$BV.configure("global",{productId : "'+productid+'"});$BV.ui("rr", "show_reviews");document.title="BV TESTING | "+document.title;</script></body>'
		bvdivs = '<div id="BVRRSummaryContainer"></div><div id="BVRRContainer"></div>'
		bvTestTitle = 'BV TESTING | '

		
		head = self.view.substr(self.view.find(r"</head>", 0, sublime.IGNORECASE))
		bodyBegin = self.view.substr(self.view.find(r"<body.*>", 0, sublime.IGNORECASE))
		body = self.view.substr(self.view.find(r"</body>", 0, sublime.IGNORECASE))
	


		content = self.view.substr(region)
		content = content.replace(head, bvapijs)
		content = content.replace(body, bvui)

		content = content.replace(bodyBegin, bodyBegin+bvdivs)
		self.view.replace(edit, region, content)