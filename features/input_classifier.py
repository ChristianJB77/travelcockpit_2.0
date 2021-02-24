import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps
from sqlalchemy import or_, func
# Database
from database.models import db, DataHubCountries, CountriesTranslate, Cities


def check(destination):
    """Check and format user input"""
    # Format user input
    try:
        dest = destination.replace("-", " ").lower()
        dest = dest.replace("_", " ")
        dest = dest.replace(",", "")
        return dest

    except (KeyError, TypeError, ValueError):
        return None

def loc_class(dest):
    """Classify location (country/city/other), trnalsate to GER and ENG"""
    dest = dest.lower()
    dest_no_space = dest.replace(" ", "")
    dest_up = dest.upper()
    dest_dic = {}

    ### Country check
    # Country check English or ISO
    if DataHubCountries.query \
            .filter(or_(func.lower(DataHubCountries.country_name) == dest, \
                func.lower(DataHubCountries.iso3166_1_alpha_2) == dest, \
                func.lower(DataHubCountries.iso316_1_alpha_3) == dest, \
                func.lower(DataHubCountries.official_name_english) == dest, \
                func.lower(DataHubCountries.iso4217_currency_country_name) \
                    == dest)).one_or_none() != None:

        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = DataHubCountries.query \
                .filter(or_(func.lower(DataHubCountries.country_name) == dest, \
                func.lower(DataHubCountries.iso3166_1_alpha_2) == dest, \
                func.lower(DataHubCountries.iso316_1_alpha_3) == dest, \
                func.lower(DataHubCountries.official_name_english) == dest, \
                func.lower(DataHubCountries.iso4217_currency_country_name) \
                    == dest)).one_or_none().iso3166_1_alpha_2.lower()

        dest_dic['countr_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().en.lower()

        # Language tag
        dest_dic['language'] = "english"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_en'].title()
        return dest_dic


    # Country check GERMAN
    elif CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest) \
            .one_or_none() != None:

        # Location type for link functions
        dest_dic['loc_type'] = "country"
        # Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
                        .filter(func.lower(CountriesTranslate.de) == dest) \
                        .one_or_none().code.lower()

        dest_dic['country_iso'] = country_iso
        # Translate to German and English
        dest_dic['country_de'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().en.lower()

        dest_dic['language'] = "german"
        # Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic


    # Replace space in German and try again
    elif CountriesTranslate.query \
            .filter(func.lower(CountriesTranslate.de) == dest_no_space) \
            .one_or_none() != None:
        dest = dest_no_space
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
                        .filter(func.lower(CountriesTranslate.de) == dest) \
                        .one_or_none().code.lower()
        dest_dic['country_iso'] = country_iso
        #Translate to German and English
        dest_dic['country_de'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().en.lower()

        dest_dic['language'] = "german"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic


    # All to upper case debugging for special character ä, ö, ü
    elif CountriesTranslate.query \
            .filter(func.upper(CountriesTranslate.de) == dest_up) \
            .one_or_none() != None:
        dest = dest_up
        #Location type for link functions
        dest_dic['loc_type'] = "country"
        #Get ISO alpha2 code
        country_iso = CountriesTranslate.query \
                        .filter(func.upper(CountriesTranslate.de) == dest) \
                        .one_or_none().code.lower()
        dest_dic['country_iso'] = country_iso
        #Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().en.lower()

        dest_dic['language'] = "german"
        #Print out for html title
        dest_dic['print'] = dest_dic['country_de'].title()
        return dest_dic


    ### City check
    # Big city check

    elif Cities.query.filter(or_( func.lower(Cities.city) == dest), \
                (func.lower(Cities.city_ascii) == dest)).one_or_none() != None:

        #Location type for link functions
        dest_dic['loc_type'] = "big_city"
        #Get city name
        city = Cities.query.filter(or_( func.lower(Cities.city) == dest), \
                    (func.lower(Cities.city_ascii) == dest)).one_or_none() \
                    .city_ascii.lower()
        dest_dic['city'] = city
        #Get ISO alpha2 code
        country_iso = Cities.query \
                    .filter(func.lower(Cities.city_ascii) == city) \
                    .one_or_none().iso2.lower()
        dest_dic['country_iso']  = country_iso
        #Translate to English and German
        dest_dic['country_de'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().de.lower()
        dest_dic['country_en'] = CountriesTranslate.query \
                            .filter(func.lower(CountriesTranslate.code) \
                            == country_iso).one_or_none().en.lower()

        dest_dic['language'] = "unclear"
        #Print out for html title
        dest_dic['print'] = dest_dic['city'].title()
        return dest_dic


    ###Good luck, country and city unknown
    else:
        dest_dic['loc_type'] = "good_luck"
        dest_dic['location'] = dest
        dest_dic['language'] = "unclear"
        #Print out for html title
        dest_dic['print'] = "Good Luck Mode for: " + dest_dic['location'].title()
        return dest_dic
