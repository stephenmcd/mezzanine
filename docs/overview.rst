.. include:: ../README.rst


Installation
============

The easiest method is to install directly from pypi using `pip`_ by
running the command below, which will also install the required
dependencies mentioned above::

    $ pip install mezzanine

If you prefer, you can download Mezzanine and install it directly from
source::

    $ python setup.py install

Once installed, the command ``mezzanine-project`` can be used to
create a new Mezzanine project in similar fashion to
``django-admin.py``::

    $ mezzanine-project project_name
    $ cd project_name
    $ python manage.py createdb --noinput
    $ python manage.py runserver

.. note::

    The ``createdb`` command is a shortcut for using Django's
    ``migrate`` command, which will also install some demo content,
    such as a contact form, image gallery, and more. If you'd like to
    omit this step, use the ``--nodata`` option with ``createdb``.

You should then be able to browse to http://127.0.0.1:8000/admin/ and
log in using the default account (``username: admin, password:
default``). If you'd like to specify a different username and password
during set up, simply exclude the ``--noinput`` option included above
when running ``createdb``.

For information on how to add Mezzanine to an existing Django project,
see the FAQ section of the documentation.

Mezzanine makes use of as few libraries as possible (apart from a
standard Django environment), with the following dependencies, which
unless noted as optional, should be installed automatically following
the above instructions:

* `Python`_ 2.7 to 3.8
* `Django`_ 1.8 to 1.11
* `django-contrib-comments`_ - for built-in threaded comments
* `Pillow`_ - for image resizing (`Python Imaging Library`_ fork)
* `grappelli-safe`_ - admin skin (`Grappelli`_ fork)
* `filebrowser-safe`_ - for managing file uploads (`FileBrowser`_ fork)
* `bleach`_ and `BeautifulSoup`_ - for sanitizing markup in content
* `pytz`_ and `tzlocal`_ - for timezone support
* `chardet`_ - for supporting arbitrary encoding in file uploads
* `django-modeltranslation`_ - for multi-lingual content (optional)
* `django-compressor`_ - for merging JS/CSS assets (optional)
* `requests`_ and `requests_oauthlib`_ - for interacting with external APIs
* `pyflakes`_ and `pep8`_ - for running the test suite (optional)

Note that various systems may contain
`specialized instructions for installing Pillow`_.

Themes
======

A handful of attractive `Free Themes`_ are available thanks to
`@abhinavsohani`_, while there is also a marketplace for buying and
selling `Premium Themes`_ thanks to `@joshcartme`_.


Browser Support
===============

Mezzanine's admin interface works with all modern browsers.
Internet Explorer 7 and earlier are generally unsupported.


Third-Party Plug-Ins
====================

The following plug-ins have been developed outside of Mezzanine. If you
have developed a plug-in to integrate with Mezzanine and would like to
list it here, send an email to the `mezzanine-users`_ mailing list, or
better yet, fork the project and create a pull request with your
plug-in added to the list below. We also ask that you add it to the
`Mezzanine Grid on djangopackages.com`_.

* `Cartridge`_ - ecommerce for Mezzanine.
* `Drum`_ - A `Hacker News`_ / `Reddit`_ clone powered by Mezzanine.
* `mezzanine-html5boilerplate`_ - Integrates the
  `html5boilerplate project`_  into Mezzanine.
* `mezzanine-mdown`_ - Adds `Markdown`_ support to Mezzanine's rich
  text editor.
* `mezzanine-openshift`_ - Setup for running Mezzanine on
  `Redhat's OpenShift`_ cloud platform.
* `mezzanine-stackato`_ - Setup for running Mezzanine on
  `ActiveState's Stackato`_ cloud platform.
* `mezzanine-blocks`_ - A Mezzanine flavored fork of
  django-flatblocks.
* `mezzanine-widgets`_ - Widget system for Mezzanine.
* `mezzanine-themes`_ - A collection of Django/Mezzanine templates.
* `mezzanine-twittertopic`_ - Manage multiple Twitter topic feeds
  from the Mezzanine admin interface.
* `mezzanine-captcha`_ - Adds CAPTCHA field types to Mezzanine's
  forms builder app.
* `mezzanine-bookmarks`_ - A multi-user bookmark app for Mezzanine.
* `mezzanine-events`_ - Events plugin for Mezzanine, with geocoding
  via Google Maps, iCalendar files, webcal URLs and directions via
  Google Calendar/Maps.
* `mezzanine-polls`_ - Polls application for Mezzanine.
* `mezzanine-pagedown`_ - Adds the `Pagedown`_ WYSIWYG editor to
  Mezzanine.
* `mezzanine-careers`_ - Job posting application for Mezzanine.
* `mezzanine-recipes`_ - Recipes plugin with built-in REST API.
* `mezzanine-slides`_ - Responsive banner slides app for Mezzanine.
* `mezzyblocks`_ - Another app for adding blocks/modules to Mezzanine.
* `mezzanine-flexipage`_ - Allows designers to manage content areas
  in templates.
* `mezzanine-instagram`_ - A simple Instagram app for Mezzanine.
* `mezzanine-wiki`_ - Wiki app for Mezzanine.
* `mezzanine-calendar`_ - Calendar pages in Mezzanine
* `mezzanine-facebook`_ - Simple Facebook integration for Mezzanine.
* `mezzanine-instagram-gallery`_ - Create Mezzanine galleries using
  Instagram images.
* `mezzanine-cli`_ - Command-line interface for Mezzanine.
* `mezzanine-categorylink`_ - Integrates Mezzanine's Link pages with
  its blog categories.
* `mezzanine-podcast`_ - A simple podcast streamer and manager for
  Mezzanine.
* `mezzanine-linkcollection`_ - Collect links. Feature them. Share
  them over RSS.
* `cash-generator`_ - Generate `GnuCash`_ invoices with Mezzanine.
* `mezzanine-foundation`_ - `Zurb Foundation`_ theme for Mezzanine.
* `mezzanine-file-collections`_ - Simple file collection page type
  for Mezzanine.
* `mezzanine-wymeditor`_ - `WYMeditor`_ adapted as the rich text
  editor for Mezzanine.
* `mezzanine-meze`_ - Adds support for `reStructuredText`_,
  `Pygments`_ and more, to Mezzanine's rich text editing.
* `mezzanine-pageimages`_ - Add background and banner images per page
  in Mezzanine.
* `mezzanine-protected-pages`_ - Restrict access to pages by group
  membership.
* `mezzanine-page-auth`_ - A Mezzanine module for add group-level
  permission to pages.
* `django-widgy`_ - Widget-oriented content editing. Includes an
  adapter for Mezzanine and a powerful form builder.
* `mezzanine-admin-backup`_ - Export your Mezzanine database and assets
  directly from the admin.
* `mezzanine-mailchimp`_ - Integrate Mezzanine forms with a MailChimp
  subscription list.
* `mezzanine-grappelli`_ - Integrates latest upstream
  grappelli/filebrowser with Mezzanine.
* `mezzanine-workout`_ - Store and display FIT data in Mezzanine.
* `mezzanine-agenda`_ - Event functionality for your Mezzanine sites.
* `mezzanine-dpaste`_ - Integrate `dpaste`_, a Django pastebin, into
  your Mezzanine site.
* `mezzanine-linkdump`_ - Create, display and track links in Mezzanine.
* `mezzanine-people`_ - Categorize and list people in Mezzanine.
* `mezzanine-webf`_ - Fabfile for deploying Mezzanine to Webfaction.
* `mezzanineopenshift`_ Another setup for `Redhat's OpenShift`_ cloud
  platform.
* `mezzanine-bsbanners`_ - Add `Twitter Bootstrap`_ Carousels and
  Jumbotrons to Mezzanine.
* `mezzanine-business-theme`_ - Starter business theme for Mezzanine.
* `open-helpdesk`_ - A helpdesk app built with Mezzanine.
* `mezzanine-invites`_ - Allow site registration via alphanumeric
  invite codes.
* `ansible-mezzanine`_ - Full pipeline (dev, staging, production)
  deployment of Mezzanine using `Ansible`_.
* `mezzanine-modal-announcements`_ - Popup announcements for Mezzanine
  websites via Bootstrap modals.
* `mezzanine-buffer`_ - `Buffer`_ integration for Mezzanine.
* `mezzanine-slideshows`_ - Allows placement of Mezzanine galleries
  within other Mezzanine pages as slideshows.
* `mezzanine-onepage`_ - Design helper for single-page Mezzanine sites.
* `mezzanine-api`_ - RESTful web API for Mezzanine.
* `mezzanine-smartling`_ - Integrates Mezzanine content with
  `Smartling Translations`_.
* `mezzanine-shortcodes`_ - `Wordpress shortcodes`_ for Mezzanine.


Sites Using Mezzanine
=====================

Got a site built with Mezzanine? You can add it to the gallery on
the `Mezzanine project page`_ by adding it to the list below - just
fork the project and create a pull request. Please omit the trailing
slash in the URL, as we manually add that ourselves to feature
certain sites.

* `Citrus Agency <http://citrus.com.au/>`_
* `Mezzanine Project <http://mezzanine.jupo.org>`_
* `Nick Hagianis <http://hagianis.com>`_
* `Thomas Johnson <http://tomfmason.net>`_
* `Central Mosque Wembley <http://wembley-mosque.co.uk>`_
* `Ovarian Cancer Research Foundation <http://ocrf.com.au/>`_
* `The Source Procurement <http://thesource.com.au/>`_
* `Imageinary <http://imageinary.com>`_
* `Brad Montgomery <http://blog.bradmontgomery.net>`_
* `Jashua Cloutier <http://www.senexcanis.com>`_
* `Alpha & Omega Contractors <http://alphaomegacontractors.com>`_
* `Equity Advance <http://equityadvance.com.au/>`_
* `Head3 Interactive <http://head3.com>`_
* `PyLadies <http://www.pyladies.com>`_
* `Ripe Maternity <http://www.ripematernity.com/>`_
* `Cotton On <http://shop.cottonon.com/>`_
* `List G Barristers <http://www.listgbarristers.com.au>`_
* `Tri-Cities Flower Farm <http://www.tricitiesflowerfarm.com>`_
* `daon.ru <http://daon.ru/>`_
* `autoindeks.ru <http://autoindeks.ru/>`_
* `immiau.ru <http://immiau.ru/>`_
* `ARA Consultants <http://www.araconsultants.com.au/>`_
* `Boîte à Z'images <http://boiteazimages.com/>`_
* `The Melbourne Cup <http://www.melbournecup.com/>`_
* `Diablo News <http://www.diablo-news.com>`_
* `Goldman Travel <http://www.goldmantravel.com.au/>`_
* `IJC Digital <http://ijcdigital.com/>`_
* `Coopers <http://store.coopers.com.au/>`_
* `Joe Julian <http://joejulian.name>`_
* `Sheer Ethic <http://sheerethic.com/>`_
* `Salt Lake Magazine <http://saltlakemagazine.com/>`_
* `Boca Raton Magazine <http://bocamag.com/>`_
* `Photog.me <http://www.photog.me>`_
* `Elephant Juice Soup <http://www.elephantjuicesoup.com>`_
* `National Positions <http://www.nationalpositions.co.uk/>`_
* `Like Humans Do <http://www.likehumansdo.com>`_
* `Connecting Countries <http://connectingcountries.net>`_
* `tindie.com <http://tindie.com>`_
* `Environmental World Products <http://ewp-sa.com/>`_
* `Ross A. Laird <http://rosslaird.com>`_
* `Etienne B. Roesch <http://etienneroes.ch>`_
* `Recruiterbox <http://recruiterbox.com/>`_
* `Mod Productions <http://modprods.com/>`_
* `Appsembler <http://appsembler.com/>`_
* `Pink Twig <http://www.pinktwig.ca>`_
* `Parfume Planet <http://parfumeplanet.com>`_
* `Trading 4 Us <http://www.trading4.us>`_
* `Chris Fleisch <http://chrisfleisch.com>`_
* `Theneum <http://theneum.com/>`_
* `My Story Chest <http://www.mystorychest.com>`_
* `Philip Sahli <http://www.fatrix.ch>`_
* `Raymond Chandler <http://www.codearchaeologist.org>`_
* `Nashsb <http://nashpp.com>`_
* `AciBASE <http://acinetobacter.bham.ac.uk>`_
* `Matthe Wahn <http://www.matthewahn.com>`_
* `Bit of Pixels <http://bitofpixels.com>`_
* `European Crystallographic Meeting <http://ecm29.ecanews.org>`_
* `Dreamperium <http://dreamperium.com>`_
* `UT Dallas <http://utdallasiia.com>`_
* `Go Yama <http://goyamamusic.com>`_
* `Yeti LLC <http://www.yetihq.com/>`_
* `Li Xiong <http://idhoc.com>`_
* `Pageworthy <http://pageworthy.com>`_
* `Prince Jets <http://princejets.com>`_
* `30 sites in 30 days <http://1inday.com>`_
* `St Barnabas' Theological College <http://www.sbtc.org.au/>`_
* `Helios 3D <http://helios3d.nl/>`_
* `Life is Good <http://lifeisgoodforall.co.uk/>`_
* `Building 92 <http://bldg92.org/>`_
* `Pie Monster <http://piemonster.me>`_
* `Cotton On Asia <http://asia.cottonon.com/>`_
* `Ivan Diao <http://www.adieu.me>`_
* `Super Top Secret <http://www.wearetopsecret.com/>`_
* `Jaybird Sport <http://www.jaybirdgear.com/>`_
* `Manai Glitter <https://manai.co.uk>`_
* `Sri Emas International School <http://www.sriemas.edu.my>`_
* `Boom Perun <http://perunspace.ru>`_
* `Tactical Bags <http://tacticalbags.ru>`_
* `apps.de <http://apps.de>`_
* `Sunfluence <http://sunfluence.com>`_
* `ggzpreventie.nl <http://ggzpreventie.nl>`_
* `dakuaiba.com <http://www.dakuaiba.com>`_
* `Wdiaz <http://www.wdiaz.org>`_
* `Hunted Hive <http://huntedhive.com/>`_
* `mjollnir.org <http://mjollnir.org>`_
* `The Beancat Network <http://www.beancatnet.org>`_
* `Raquel Marón <http://raquelmaron.com/>`_
* `EatLove <http://eatlove.com.au/>`_
* `Hospitality Quotient <http://hospitalityq.com/>`_
* `The Andrew Story <http://theandrewstory.com/>`_
* `Charles Koll Jewelry <http://charleskoll.com/>`_
* `Creuna (com/dk/fi/no/se) <http://www.creuna.com/>`_
* `Coronado School of the Arts <http://www.cosasandiego.com/>`_
* `SiteComb <http://www.sitecomb.com>`_
* `Dashing Collective <http://dashing.tv/>`_
* `Puraforce Remedies <http://puraforceremedies.com/>`_
* `Google's VetNet <http://www.vetnethq.com/>`_
* `1800RESPECT <http://www.1800respect.org.au/>`_
* `Evenhouse Consulting <http://evenhouseconsulting.com/>`_
* `Humboldt Community Christian School <http://humboldtccs.org>`_
* `Atlanta's Living Legacy <http://gradyhistory.com>`_
* `Shipgistix <http://shipgistix.com>`_
* `Yuberactive <http://www.yuberactive.asia>`_
* `Medical Myth Busters <http://pogromcymitowmedycznych.pl>`_
* `4player Network <http://4playernetwork.com/>`_
* `Top500 Supercomputers <http://top500.org>`_
* `Die Betroffenen <http://www.zeichnemit.de>`_
* `uvena.de <http://uvena.de>`_
* `ezless.com <http://ezless.com>`_
* `Dominican Python <http://python.do>`_
* `Stackful.io <http://stackful.io/>`_
* `Adrenaline <http://www.adrln.com/>`_
* `ACE EdVenture Programme <http://aceedventure.com/>`_
* `Butchershop Creative <http://www.butchershopcreative.com/>`_
* `Sam Kingston <http://www.sjkingston.com>`_
* `Ludwig von Mises Institute <http://mises.fi>`_
* `Incendio <http://incendio.no/>`_
* `Alexander Lillevik <http://lillevikdesign.no/>`_
* `Walk In Tromsø <http://www.turitromso.no>`_
* `Mandrivia Linux <http://www.mandriva.com/>`_
* `Crown Preschool <http://crownpreschool.com>`_
* `Coronado Pathways Charter School <http://coronadopathways.com>`_
* `Raindrop Marketing <http://www.raindropads.com>`_
* `Web4py <http://www.web4py.com>`_
* `The Peculiar Store <http://thepeculiarstore.com>`_
* `GrinDin <http://www.grindin.ru>`_
* `4Gume <http://www.4gume.com>`_
* `Skydivo <http://skydivo.com>`_
* `Noshly <http://noshly.com>`_
* `Kabu Creative <http://kabucreative.com.au/>`_
* `KisanHub <http://www.kisanhub.com/>`_
* `Your Song Your Story <http://yoursongyourstory.org/>`_
* `Kegbot <http://kegbot.org>`_
* `Fiz <http://fiz.com/>`_
* `Willborn <http://willbornco.com>`_
* `Copilot Co <http://copilotco.com>`_
* `Amblitec <http://www.amblitec.com>`_
* `Gold's Gym Utah <http://www.bestgymever.com/>`_
* `Appsin - Blog to Native app <http://apps.in/>`_
* `Take Me East <http://takemeeast.net>`_
* `Code Raising <http://www.coderaising.org>`_
* `ZigZag Bags <http://www.zigzagbags.com.au>`_
* `VerifIP <http://verifip.com/>`_
* `Clic TV <http://www.clictv.tv/>`_
* `JE Rivas <http://www.jerivas.com/>`_
* `Heather Gregory Nutrition <http://heathergregorynutrition.com>`_
* `Coronado Island Realty <http://coronado-realty.com>`_
* `Loans to Homes <http://loanstohomes.com>`_
* `Gensler Group <http://genslergroup.com>`_
* `SaniCo <https://sanimedicaltourism.com>`_
* `Grupo Invista <http://grupoinvista.com>`_
* `Brooklyn Navy Yard <http://brooklynnavyyard.org/>`_
* `MEZZaTHEME <http://mezzathe.me/>`_
* `Nektra Advanced Computing <http://www.nektra.com/>`_
* `Bootstrap ASAP <https://bootstrapasap.com/>`_
* `California Center for Jobs <http://www.centerforjobs.org/>`_
* `Sam Kingston <http://www.sjkingston.com>`_
* `Code Juggle DJ <http://www.codejuggle.dj>`_
* `Food News <http://food.hypertexthero.com>`_
* `Australian Discworld Conventions <http://ausdwcon.org>`_
* `Distilled <http://www.distilled.net/>`_
* `OpenMRP <http://www.openmrp.es>`_
* `Arkade Snowboarding <http://www.arkadesnowboarding.com/>`_
* `Linktective The Link Checker <http://www.linktective.com>`_
* `Zetalab <http://www.zetalab.de>`_
* `Make-Up Artists & Hair Stylists Guild <http://www.local706.org>`_
* `Anywhereism <http://www.anywhereism.net>`_
* `Assistive Listening Device Locator <http://aldlocator.com>`_
* `Frank & Connie Spitzer <http://sdhome4you.com>`_
* `Coronado Unified School District <http://coronadousd.net>`_
* `Coronado Inn <http://coronadoinn.com>`_
* `Coronado Schools Foundation <http://csfkids.org>`_
* `Light and Life Christian School <http://www.lightandlifechristianschool.com>`_
* `The Morabito Group <http://themorabitogroup.com>`_
* `Law Offices of Nancy Gardner <http://nancygardnerlaw.com>`_
* `Soden & Steinberger APLC <http://legalmattersllp.com>`_
* `Stalwart Communications <http://stalwartcom.com>`_
* `Ubuntu Consultants <http://ubuntuconsultants.com>`_
* `Wine a Bit Coronado <http://wineabitcoronado.com>`_
* `Mercury Mastering <http://mercurymastering.com>`_
* `Flowgrammable <http://flowgrammable.org>`_
* `Shibe Mart <http://shibemart.com>`_
* `Carlos Isaac Balderas <http://caisbalderas.com/>`_
* `Enrico Tröger <http://www.pending.io>`_
* `Perugini <http://peruginicase.it/>`_
* `YouPatch <https://www.youpatch.com>`_
* `Batista Peniel <http://batistapeniel.org>`_
* `Perceptyx <http://www.perceptyx.com/>`_
* `Guddina Coffee <http://guddina.com>`_
* `Atami Escape Resort <http://www.atami.com.sv>`_
* `Philip Southwell <http://www.philipsouthwell.com>`_
* `Justine & Katie's Bowtique <http://www.jnkbows.com>`_
* `The Grantwell LLC <https://www.thegrantwell.com>`_
* `PyCon Asia-Pacific <https://tw.pycon.org/>`_
* `Nerdot <http://nerdot.com.do>`_
* `Coworking.do <http://coworking.do>`_
* `Arlette Pichardo <http://arlettepichardo.com>`_
* `Sani Dental Group <http://sanidentalgroup.com>`_
* `Biocap 06 <http://www.biocap06.fr>`_
* `Python Baja California <http://pythonbc.co/>`_
* `The Art Rebellion <http://www.theartrebellion.com/>`_
* `Engineered Arts <https://www.engineeredarts.co.uk>`_
* `Paul Whipp Consulting <http://www.paulwhippconsulting.com>`_
* `Lipman Art <https://lipmanart.com/>`_
* `MODCo Group <http://modcogroup.com/>`_
* `Terminal Labs <http://www.terminallabs.com>`_
* `Resource Management Companies <http://rmcrecycle.com>`_
* `DollFires <http://dollfires.com>`_
* `Quantifind <http://quantifind.com/>`_
* `ZHackers <https://www.zhackers.com>`_
* `Open ERP Arabia <http://openerparabia.org/>`_
* `DataKind <http://www.datakind.org/>`_
* `New Zealand Institute of Economic Research <http://nzier.org.nz/>`_
* `CodingHouse <http://thecodinghouse.in>`_
* `Triple J Products <http://triplejcoilproducts.com>`_
* `Aaron E. Balderas <http://abalderas.com>`_
* `DVD.nl <http://dvd.nl/>`_
* `Constantia Fabrics <http://www.constantiafabrics.co.za/>`_
* `Potrillo al Pie <http://potrilloalpie.com/>`_
* `Skyfalk Web Studio <http://skyfalk.ru>`_
* `Firefox OS Partners <https://mobilepartners.mozilla.org/>`_
* `You Name It <http://you-name-it.net>`_
* `Atlas of Human Infectious Diseases <https://infectionatlas.org>`_
* `The Entrepreneurial School <http://theentrepreneurialschool.com/>`_
* `Wednesday Martin <http://wednesdaymartin.com/>`_
* `Avaris to Avanim <https://avaristoavanim.com>`_
* `Cognitions Coaching and Consulting <http://www.cognitionscoachingandconsulting.com>`_
* `Foundation Engineering Group <http://fegroup.net.au>`_
* `Hivelocity <https://www.hivelocity.net>`_
* `Zooply <http://zoop.ly>`_
* `Oceana Technologies <http://oceanatech.com>`_
* `TerraHub <http://terrahub.org/>`_
* `djangoproject.jp <http://djangoproject.jp/>`_
* `Joshua Ginsberg <http://starboard.flowtheory.net>`_
* `Savant Digital <http://www.savantdigital.net>`_
* `weBounty <https://webounty.com>`_
* `Oxfam America <http://www.oxfamamerica.org/>`_
* `Artivest <https://artivest.co/>`_
* `Dark Matter Sheep <http://darkmattersheep.net>`_
* `Mission Healthcare <http://homewithmission.com>`_
* `Two Forty Fives <http://twofortyfives.com/>`_
* `Rodeo Austin <http://rodeoaustin.com/>`_
* `Krisers <http://krisers.com/>`_
* `Intentional Creation <http://intentionalcreation.com/>`_
* `BytesArea <http://www.bytesarea.com>`_
* `Debra Solomon <http://www.debrasolomon.com>`_
* `Pampanga Food Company <http://pampangafood.com>`_
* `Aman Sinaya <http://amansinaya.com>`_
* `Deschamps osteo <http://www.deschamps-osteopathe.fr>`_
* `Deschamps kine <http://www.deschamps-kinesitherapeute.fr>`_
* `Creactu <http://creactu.fr>`_
* `scrunch <https://scrunch.com>`_
* `App Dynamics <http://www.appdynamics.com/>`_
* `Homespun Music Instruction <https://www.homespun.com>`_
* `Fusionbox <https://www.fusionbox.com/>`_
* `The Street University <http://www.streetuni.net>`_
* `Glebe <http://glebe.com.au>`_
* `CeoDental Seminars <https://www.ceodental.com.au>`_
* `Pay By Super <https://www.paybysuper.com.au>`_
* `Noffs <https://www.noffs.org.au>`_
* `Spokade <http://spokade.com>`_
* `Brisbane Prosthodontics <http://www.brisbaneprosthodontics.com.au>`_
* `Carbonised <http://carbonised.com.au>`_
* `Derry Donnell <http://www.derrydonnell.com.au>`_
* `Dr Kenneth Cutbush <http://kennethcutbush.com>`_
* `American Institute for Foreign Study <http://www.aifs.com.au>`_
* `Camp America <http://campamerica.com.au>`_
* `Code Source <http://codesource.com.au/>`_
* `The Federation of Egalitarian Communities <http://thefec.org>`_
* `Caffeinated Lifestyle <https://caffeinatedlifestyle.com>`_
* `The National: New Australian Art <https://the-national.com.au>`_

.. _`Mezzanine Grid on djangopackages.com`: http://www.djangopackages.com/grids/g/mezzanine/
.. _`Cartridge`: http://cartridge.jupo.org/
.. _`Drum`: https://github.com/stephenmcd/drum
.. _`Hacker News`: https://news.ycombinator.com
.. _`Reddit`: http://www.reddit.com
.. _`mezzanine-html5boilerplate`: https://github.com/tvon/mezzanine-html5boilerplate
.. _`mezzanine-html5boilerplate`: https://github.com/tvon/mezzanine-html5boilerplate
.. _`html5boilerplate project`: http://html5boilerplate.com/
.. _`mezzanine-mdown`: https://bitbucket.org/onelson/mezzanine-mdown
.. _`Markdown`: http://en.wikipedia.org/wiki/Markdown
.. _`mezzanine-openshift`: https://github.com/overshard/mezzanine-openshift
.. _`Redhat's OpenShift`: https://openshift.redhat.com/
.. _`Ansible`: http://www.ansible.com/
.. _`mezzanine-stackato`: https://github.com/Stackato-Apps/mezzanine
.. _`ActiveState's Stackato`: http://www.activestate.com/stackato
.. _`mezzanine-blocks`: https://github.com/renyi/mezzanine-blocks
.. _`mezzanine-widgets`: https://github.com/osiloke/mezzanine_widgets
.. _`mezzanine-themes`: https://github.com/renyi/mezzanine-themes
.. _`mezzanine-twittertopic`: https://github.com/lockhart/mezzanine-twittertopic
.. _`mezzanine-captcha`: https://github.com/mjtorn/mezzanine-captcha
.. _`mezzanine-bookmarks`: https://github.com/adieu/mezzanine-bookmarks
.. _`mezzanine-events`: https://github.com/stbarnabas/mezzanine-events
.. _`mezzanine-polls`: https://github.com/sebasmagri/mezzanine_polls
.. _`mezzanine-pagedown`: https://bitbucket.org/akhayyat/mezzanine-pagedown
.. _`PageDown`: https://code.google.com/p/pagedown/
.. _`mezzanine-careers`: https://github.com/mogga/mezzanine-careers
.. _`mezzanine-recipes`: https://github.com/tjetzinger/mezzanine-recipes
.. _`mezzanine-slides`: https://github.com/overshard/mezzanine-slides
.. _`mezzyblocks`: https://github.com/jardaroh/mezzyblocks
.. _`mezzanine-flexipage`: https://github.com/mrmagooey/mezzanine-flexipage
.. _`mezzanine-wiki`: https://github.com/dfalk/mezzanine-wiki
.. _`mezzanine-instagram`: https://github.com/shurik/Mezzanine_Instagram
.. _`mezzanine-calendar`: https://github.com/shurik/mezzanine.calendar
.. _`mezzanine-facebook`: https://github.com/shurik/Mezzanine_Facebook
.. _`mezzanine-instagram-gallery`: https://github.com/georgeyk/mezzanine-instagram-gallery
.. _`mezzanine-cli`: https://github.com/adieu/mezzanine-cli
.. _`mezzanine-categorylink`: https://github.com/mjtorn/mezzanine-categorylink
.. _`mezzanine-podcast`: https://github.com/carpie/mezzanine-podcast
.. _`mezzanine-linkcollection`: https://github.com/mjtorn/mezzanine-linkcollection
.. _`cash-generator`: https://github.com/ambientsound/cash-generator
.. _`GnuCash`: http://www.gnucash.org/
.. _`mezzanine-foundation`: https://github.com/zgohr/mezzanine-foundation
.. _`Zurb Foundation`: http://foundation.zurb.com/
.. _`mezzanine-file-collections`: https://github.com/thibault/mezzanine-file-collections
.. _`mezzanine-wymeditor`: https://github.com/excieve/mezzanine-wymeditor
.. _`WYMeditor`: http://wymeditor.github.io/wymeditor/
.. _`mezzanine-meze`: https://github.com/abakan/mezzanine-meze
.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`Pygments`: http://pygments.org/
.. _`mezzanine-pageimages`: https://github.com/bcs-de/mezzanine-pageimages
.. _`mezzanine-protected-pages`: https://github.com/evilchili/mezzanine-protected-pages
.. _`mezzanine-page-auth`: https://github.com/simodalla/mezzanine_page_auth
.. _`django-widgy`: http://django-widgy.readthedocs.org/en/latest/
.. _`mezzanine-admin-backup`: https://bitbucket.org/joshcartme/mezzanine-admin-backup
.. _`mezzanine-mailchimp`: https://bitbucket.org/naritas/mezzanine-mailchimp
.. _`mezzanine-grappelli`: https://github.com/sephii/mezzanine-grappelli
.. _`mezzanine-workout`: https://github.com/kampfschlaefer/mezzanine-workout
.. _`mezzanine-agenda`: https://github.com/jpells/mezzanine-agenda
.. _`mezzanine-dpaste`: https://github.com/prikhi/mezzanine-dpaste
.. _`mezzanine-linkdump`: https://github.com/prikhi/mezzanine-linkdump
.. _`mezzanine-people`: https://github.com/eci/mezzanine-people
.. _`mezzanine-webf`: https://github.com/jerivas/mezzanine-webf
.. _`mezzanineopenshift`: https://bitbucket.org/radeksvarz/mezzanineopenshift
.. _`mezzanine-bsbanners`: https://pypi.python.org/pypi/mezzanine-bsbanners
.. _`mezzanine-business-theme`: https://github.com/dfalk/mezzanine-business-theme
.. _`open-helpdesk`: https://github.com/simodalla/open-helpdesk
.. _`mezzanine-invites`: https://github.com/averagehuman/mezzanine-invites
.. _`ansible-mezzanine`: https://github.com/keithadavidson/ansible-mezzanine
.. _`mezzanine-modal-announcements`: https://github.com/joshcartme/mezzanine-modal-announcements
.. _`mezzanine-buffer`: https://github.com/caffodian/mezzanine-buffer
.. _`Buffer`: http://buffer.com
.. _`mezzanine-slideshows`: https://github.com/philipsouthwell/mezzanine-slideshows
.. _`mezzanine-onepage`: https://github.com/lucmilland/mezzanine-onepage
.. _`mezzanine-api`: https://github.com/gcushen/mezzanine-api
.. _`mezzanine-smartling`: https://github.com/Appdynamics/mezzanine-smartling
.. _`mezzanine-shortcodes`: https://github.com/ryneeverett/mezzanine-shortcodes

.. _`Wordpress shortcodes`: https://codex.wordpress.org/Shortcode
.. _`Smartling Translations`: http://www.smartling.com/
.. _`dpaste`: https://github.com/bartTC/dpaste


.. _`Python`: http://python.org/
.. _`django-contrib-comments`: https://pypi.python.org/pypi/django-contrib-comments
.. _`bleach`: http://pypi.python.org/pypi/bleach
.. _`BeautifulSoup`: http://www.crummy.com/software/BeautifulSoup/
.. _`pytz`: http://pypi.python.org/pypi/pytz/
.. _`tzlocal`: http://pypi.python.org/pypi/tzlocal/
.. _`django-compressor`: https://pypi.python.org/pypi/django_compressor
.. _`Python Imaging Library`: http://www.pythonware.com/products/pil/
.. _`Pillow`: https://github.com/python-imaging/Pillow
.. _`grappelli-safe`: http://github.com/stephenmcd/grappelli-safe
.. _`filebrowser-safe`: http://github.com/stephenmcd/filebrowser-safe/
.. _`Grappelli`: http://code.google.com/p/django-grappelli/
.. _`FileBrowser`: http://code.google.com/p/django-filebrowser/
.. _`pip`: http://www.pip-installer.org/
.. _`requests`: http://docs.python-requests.org/en/latest/
.. _`requests_oauthlib`: http://requests-oauthlib.readthedocs.org/
.. _`pyflakes`: http://pypi.python.org/pypi/pyflakes
.. _`chardet`: https://chardet.readthedocs.org
.. _`pep8`: http://pypi.python.org/pypi/pep8
.. _`specialized instructions for installing Pillow`: https://pillow.readthedocs.io/en/latest/installation.html
.. _`Homebrew`: http://mxcl.github.com/homebrew/
.. _`django-modeltranslation`: http://django-modeltranslation.readthedocs.org
