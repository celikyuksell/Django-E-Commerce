# -*- coding: utf-8 -*-
import sys, os
import logging
from xml.etree import ElementTree as ET
from requests import get, exceptions
from datetime import datetime

from ._currencyhandler import BaseHandler

if sys.version_info.major == 2:
    FileNotFoundError = IOError


class CurrencyHandler(BaseHandler):
    """
    Currency Handler implements public API:
    name
    endpoint
    get_allcurrencycodes()
    get_currencyname(code)
    get_info(code)
    """
    name = 'currency-iso.org'
    endpoint = 'http://www.currency-iso.org/dam/downloads/lists/list_one.xml'

    _cached_currency_file = os.path.join(BaseHandler._dir, '_currencyiso.xml')

    _currencies = None
    published = None

    @property
    def currencies(self):
        if self._currencies is None:
            self._currencies = self.get_currencies()
            self.published = self._check_doc(self._currencies)
        return self._currencies

    def get_currencies(self):
        """Downloads xml currency data or if not available tries to use cached file copy"""
        try:
            resp = get(self.endpoint)
            resp.raise_for_status()
        except exceptions.RequestException as e:
            self.log(logging.ERROR, "%s: Problem whilst contacting endpoint:\n%s", self.name, e)
        else:
            with open(self._cached_currency_file, 'wb') as fd:
                fd.write(resp.content)

        try:
            root = ET.parse(self._cached_currency_file).getroot()
        except FileNotFoundError as e:
            raise RuntimeError("%s: XML not found at endpoint or as cached file:\n%s" % (self.name, e))

        return root

    def _check_doc(self, root):
        """Validates the xml tree and returns the published date"""
        if (root.tag != 'ISO_4217' or
            root[0].tag != 'CcyTbl' or
            root[0][0].tag != 'CcyNtry' or
            not root.attrib['Pblshd'] or
            # Actual length in Oct 2016: 279
            len(root[0]) < 270):

            raise TypeError("%s: XML %s appears to be invalid" % (self.name, self._cached_currency_file))

        return datetime.strptime(root.attrib['Pblshd'], '%Y-%m-%d').date()

    def get_allcurrencycodes(self):
        """Return an iterable of distinct 3 character ISO 4217 currency codes"""
        foundcodes = []
        codeelements = self.currencies[0].iter('Ccy')
        for codeelement in codeelements:
            code = codeelement.text
            if code not in foundcodes:
                foundcodes += [code]
                yield code

    def get_currency(self, code):
        """
        Returns an iterable of currency elements matching the code:
        <CtryNm>UNITED STATES MINOR OUTLYING ISLANDS (THE)</CtryNm>
        <CcyNm>US Dollar</CcyNm>
        <Ccy>USD</Ccy>
        <CcyNbr>840</CcyNbr>
        <CcyMnrUnts>2</CcyMnrUnts>
        NOTE: the currency is repeated for each country name
        """
        missing = True
        for currency in self.currencies[0]:
            try:
                if code != currency.find('Ccy').text:
                    continue
            except AttributeError:
                continue

            missing = False
            yield currency

        if missing:
            raise RuntimeError("%s: %s not found" % (self.name, code))

    def get_currencyname(self, code):
        """Return the currency name from the code"""
        return next(self.get_currency(code)).find('CcyNm').text

    def get_info(self, code):
        """Return a dict of information about the currency"""
        for i, currency in enumerate(self.get_currency(code)):
            if i == 0:
                try:
                    exp = int(currency.find('CcyMnrUnts').text)
                except ValueError:
                    exp = 0
                info = {
                    'CountryNames': [],
                    'ISO4217Number': int(currency.find('CcyNbr').text),
                    'ISO4217Exponent': exp,
                    'ISOUpdate': self.published.isoformat(),
                }
            try:
                ctry_name = currency.find('CtryNm').text
            except AttributeError:
                continue
            if ctry_name:
                info['CountryNames'] += [ctry_name]
        return info
