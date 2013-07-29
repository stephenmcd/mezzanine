��          �      \      �     �  �   �  �  �     +  J   /     z     �    �  3   �     �     �     �     �     �     �                     .  �  A  �   .	  �   .
  �  �
     o  F   w     �     �    �  P   �     &     4     ;     B     b     g     m     �     �  
   �        	      
                                                                                     A sequence of IDs from the ``PAGE_MENU_TEMPLATES`` setting that defines the default menu templates selected when creating new pages. By default all menu templates are selected. Set this setting to an empty sequence to have no templates selected by default. A sequence of ``Page`` subclasses in the format ``app_label.model_name``, that controls the ordering of items in the select drop-down for adding new pages within the admin page tree interface. A sequence of templates used by the ``page_menu`` template tag. Each item in the sequence is a three item sequence, containing a unique ID for the template, a label for the template, and the template path. These templates are then available for selection when editing which menus a page should appear in. Note that if a menu template is used that doesn't appear in this setting, all pages will appear in it. Add An error occured with the following class. Does it subclass Page directly? Footer Home If ``True``, pages with ``login_required`` checked will still be listed in menus and search results, for unauthenticated users. Regardless of this setting, when an unauthenticated user accesses a page with ``login_required`` checked, they'll be redirected to the login page. If checked, only logged in users can view this page Left-hand tree Link Links Login required Page Pages Rich text page Rich text pages Show in menus Top navigation bar Project-Id-Version: Mezzanine
Report-Msgid-Bugs-To: https://github.com/stephenmcd/mezzanine/issues
POT-Creation-Date: 2013-04-07 09:34-0430
PO-Revision-Date: 2013-07-29 16:05+0200
Last-Translator: hkoivuneva <henri.koivuneva@gmail.com>
Language-Team: Finnish (http://www.transifex.com/projects/p/mezzanine/language/fi/)
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: fi
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 1.5.7
 ID-sarja asetuksesta ``PAGE_MENU_TEMPLATES`` joka määrittää oletuspohjat valikoilla jotka valitaan kun uusia sivuja luodaan. Oletuksena kaikki valikkopohjat ovat valittuina. Aseta tämä tyhjäksi jos haluat että mitään pohjia ei valita oletuksena. Sarja ``Page`` aliluokkia muodossa ``app_label.model_name``, joka hallitsee kohteiden järjestystä valinta-pudotusvalikossa jolla lisätään uusia sivuja hallintapaneelin kautta. Sarja sivupohjia joita ``page_menu`` template tag käyttää. Jokainen kohta sarjassa on kolmen kohdan sarja, sisältäen uniikin ID:n sivupohjalle, sen tunnisteen ja polun. Nämä sivupohjat ovat sitten saatavilla valittavaksi kun muokataan missä valikoissa sivun tulisi näkyä. Huomaa että jos valikkopohja on käytössä eikä sitä näy tässä asetuksessa, kaikki sivut näkyvät siinä. Lisää Virhe kohdattiin seuraavalla luokalla. Aliluokittaako se Sivun oikein? Alaosa Etusivu Jos ``Tosi``, sivut joilla on ``login_required`` valittuna näytetään valikoissa ja hakutuloksissa käyttäjille joilla ei ole vaadittuja oikeuksia. Kuitenkin jos hän avaa sivun jolla on ``login_required`` valittuna, hänet ohjataan sisäänkirjautumissivulle. Jos valittu, vain sisäänkirjautuneet käyttäjät voivat nähdä tämän sivun Vasen valikko linkki Linkit Sisäänkirjautuminen vaaditaan Sivu Sivut Sisällöllinen sivu Sisällölliset sivut Näytä valikoissa Yläpalkki 