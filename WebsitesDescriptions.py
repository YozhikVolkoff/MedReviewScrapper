"""
Проблемные препараты: 
    1. на Отзовике:
        - глицин (сделать ссылки)
        - валериана (ищет всякую ерунду)
        - антигриппин (немного ерунды)
        - аргоферон – видимо, эргоферон. 
    С отзовиком вообще проблемы – он меня банит, и банит надолго. Таймаут – минута.
    2. на iRecommend:                                                               
        - валериана (ищется просто все, от книг до актеров) - добавил "средство"     \ 
        - анаферон (нагрудник для кормления) – добавил средство                       \ 
        - кагоцел (масло для губ) - добавил средство                                   } DONE
        - глицин (ищется много) – добавил средство                                    /
        - ацикловир (много на второй странице) - добавил отдельные ссылки            /
        Для этого же сайта добавил список additional_refs_to_drugs, потому что эти drugs 
        из-за слова "средство" выпадают.
"""

irecommend_structure = {
    'medicine_search_rule': "/srch?query=",
    'site_ref': "https://irecommend.ru",
    'page_search_rule': ["?page=", ""],
    'parser': 'lxml',
    'timeout': 30,

    'drug_tag_list': ["ul", {"class": "srch-result-nodes"}],
    'drug_item': ["li", {}],
    'drug_title': ["div", {"class": "title"}],
    'drug_reviews_amount': ["span", {"class": "counter"}],

    'review_list_tag_list': ["ul", {"class": "list-comments"}],
    'review_list_item': ["li", {}],
    'review_list_title': ["div", {"class": "reviewTitle"}],
    'review_list_items_on_page': 50,

    'review_title': ["a", {"class": "review-summary active"}],
    'review_body': ["div", {"class": "views-field-teaser reviewText"}],

    'banned_refs_to_drugs': []
}

otzovik_structure = {
    'medicine_search_rule': "/?search_text=",
    'site_ref': "https://otzovik.com",
    'page_search_rule': ["/", "/"],
    'parser': 'lxml',
    'timeout': 60,

    'drug_tag_list': ["tbody", {}],
    'drug_item': ["tr", {"class": "item sortable"}],
    'drug_title': ["div", {"class": ["product-photo has-photo", "product-photo nophoto"]}],
    'drug_reviews_amount': ["a", {"class": "reviews-counter"}],

    'review_list_tag_list': ["div", {"class": "review-list-2 review-list-chunk"}],
    'review_list_item': ["div", {"class": "item-right"}],
    'review_list_title': ["h3", {}],
    'review_list_items_on_page': 20,

    'review_title': ["h1", {}],
    'review_body': ["div", {"class": "review-body description"}],

    # Валериана, глицин, антигриппин содержат нерелевантные ответы. Поэтому для них –
    # banned_refs_to_drugs.

    'banned_refs_to_drugs': ["/reviews/gemeopaticheskiy_preparat_radograd_kedroviy_antigrippin/",
                             "/reviews/aromatizirovannaya_sol_s_penoy_dlya_vann_prirodnaya_apteka_valeriana_i_pustirnik/",
                             "/reviews/valeriani_kornevischa_s_kornyami_zdorove_20_filtr-paketikov/",
                             "/reviews/dekorativnoe_kashpo_iz_keramiki_dlya_cvetov_valerian_arfa/",
                             "/reviews/drazhe_uspokoitelnoe_parafarm_vechernee_plyus_valeriana_pustirnik/",
                             "/reviews/fitochay_altayskiy_kedr_krepkie_nervi_s_valerianoy/",
                             "/reviews/zhir_ribniy_s_ekstraktami_valeriani_i_pustirnika_bio_kontur/",
                             "/reviews/celebnie_travi_narodnaya_medicina_kornevischa_valeriani/",
                             "/reviews/filtr-paketi_altay-farm_valeriana_s_romashkoy/",
                             "/reviews/dieticheskaya_dobavka_v_kaplyah_valeriana/",
                             "/reviews/ribiy_zhir_biafishenol_s_valerianoy_i_pustirnikom/",
                             "/reviews/bad_k_pische_fitolyuks-4_mirosedarin_s_valerianoy/",
                             "/reviews/maslo_dlya_vann_kneipp_c_valerianoy_i_hmelem/",
                             "/reviews/travyanoy_sbor_filtr-paketi_farm_grupp_valeriana_s_romashkoy/",
                             "/reviews/fito_chay_klyuchi_zdorovya_valeriana/",
                             "/reviews/antistress_sol_sbc_aromatizirovannaya_s_penoy_dlya_vanni_valeriana_i_pustirnik/",
                             "/reviews/skrab_valeriana_chudo_lukoshko/",
                             "/reviews/bad_mirrolla_ribiy_zhir_s_valerianoy_i_pustirnikom/",
                             "/reviews/film_valerian_i_gorod_tisyachi_planet_2017/",
                             "/reviews/fitochay_naturofarm_valeriana_boyarishnik_zveroboy/",
                             "/reviews/sol_dlya_vann_vkusvill_valeriana_i_solodka/",
                             "/reviews/komiks_valerian_i_lorreyn-per_kristin_zhan-klod_mezer/",
                             "/reviews/balzam_zolotoy_altay_s_melissoy_i_valerianoy_antistress/",
                             "/reviews/kniga_godi_tropi_ruzhe-valerian_pravduhin/",
                             "/reviews/kniga_stranniy_bal-valerian_olin/",
                             "/reviews/penka_dlya_umivaniya_bielita-viteks_delikatnoe_ochischenie_tonizirovanie_s_glicinom_i_lemongrassom/",
                             "/reviews/sup_momentalnogo_prigotovleniya_pikantniy_herbal_active_obogaschenniy_glicinom_i_ekstraktom_chesnoka/",
                             "/reviews/maska-plenka_snimayuschayasya_bielita-viteks_glubokoe_ochischenie_podtyagivanie_s_glicinom_i_lemongrassom/",
                             "/reviews/maska-plenka_dlya_lica_viteks_s_glicinom_i_lemongrassom/",
                             "/reviews/magazin_sazhencev_gliciniya_russia_krim/",
                             "/reviews/gel_obogaschenniy_tiande_s_argininom_i_glicinom/",
                             "/reviews/zhevatelnaya_rezinka_evalar_glicin/",
                             "/reviews/zhevatelnaya_rezinka_smartgum_glicin/",
                             "/reviews/dieticheskaya_dobavka_tabula_vita_glicin/",
                             "/reviews/glirikum_glicin_plus_vitamini_v/",
                             "/reviews/shipuchie_tabletki_evalar_glicin_forte/"]
}
