# -*- coding: utf-8 -*-
import re
from pysbd.abbreviation_replacer import AbbreviationReplacer
from pysbd.between_punctuation import BetweenPunctuation
from pysbd.lang.common import Common, Standard
from pysbd.processor import Processor
from pysbd.utils import Text
from pysbd.punctuation_replacer import replace_punctuation
from pysbd.lists_item_replacer import ListItemReplacer

class French(Common, Standard):

    iso_code = 'fr'

    class ListItemReplacer(ListItemReplacer):

        def add_line_break(self):
            # We've found alphabetical lists are causing a lot of problems with abbreviations
            # with multiple periods and spaces, such as 'Company name s. r. o.'. Disabling
            # alphabetical list parsing seems like a reasonable tradeoff.

            self.format_alphabetical_lists()
            self.format_roman_numeral_lists()
            self.format_numbered_list_with_periods()
            self.format_numbered_list_with_parens()
            return self.text

    class AbbreviationReplacer(AbbreviationReplacer):
        SENTENCE_STARTERS = []
        def replace_period_of_abbr(self, txt, abbr):
            abbr_new = abbr.replace(".", "∯") + "∯"
            txt = txt.replace(abbr + ".", abbr_new)
            return txt

    class Abbreviation(Standard.Abbreviation):
        ABBREVIATIONS = ['a.c.n', 'a.m', 'al', 'ann', 'apr', 'art', 'auj', 'av', 'b.p', 'boul', 'c.-à-d', 'c.n', 'c.n.s', 'c.p.i', 'c.q.f.d', 'c.s', 'ca', 'cf', 'ch.-l', 'chap', 'co', 'co', 'contr', 'dir', 'e.g', 'e.v', 'env', 'etc', 'ex', 'fasc', 'fig', 'fr', 'fém', 'hab', 'i.e', 'ibid', 'id', 'inf', 'l.d', 'lib', 'll.aa', 'll.aa.ii', 'll.aa.rr', 'll.aa.ss', 'll.ee', 'll.mm', 'll.mm.ii.rr', 'loc.cit', 'ltd', 'ltd', 'masc', 'mm', 'ms', 'n.b', 'n.d', 'n.d.a', 'n.d.l.r', 'n.d.t', 'n.p.a.i', 'n.s', 'n/réf', 'nn.ss', 'p.c.c', 'p.ex', 'p.j', 'p.s', 'pl', 'pp', 'r.-v', 'r.a.s', 'r.i.p', 'r.p', 's.a', 's.a.i', 's.a.r', 's.a.s', 's.e', 's.m', 's.m.i.r', 's.s', 'sec', 'sect', 'sing', 'sq', 'sqq', 'ss', 'suiv', 'sup', 'suppl', 't.s.v.p', 'tél', 'vb', 'vol', 'vs', 'x.o', 'z.i', 'éd', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        PREPOSITIVE_ABBREVIATIONS = []
        NUMBER_ABBREVIATIONS = []

    class BetweenPunctuation(BetweenPunctuation): #TODO refactor this class

        def sub_punctuation_between_quotes_and_parens(self, txt):
            txt = self.sub_punctuation_between_single_quotes(txt)
            txt = self.sub_punctuation_between_single_quote_slanted(txt)
            txt = self.sub_punctuation_between_double_quotes(txt)
            txt = self.sub_punctuation_between_square_brackets(txt)
            txt = self.sub_punctuation_between_parens(txt)
            txt = self.sub_punctuation_between_quotes_arrow(txt)
            txt = self.sub_punctuation_between_em_dashes(txt)
            txt = self.sub_punctuation_between_quotes_slanted(txt)
            return txt

    class Processor(Processor):

        def __init__(self, text, lang, char_span=False):
            super().__init__(text, lang, char_span)

        def process(self):
            if not self.text:
                return self.text
            self.text = self.text.replace('\n', '\r')

            # Here we use language specific ListItemReplacer:
            li = self.lang.ListItemReplacer(self.text)
            self.text = li.add_line_break()

            self.replace_abbreviations()
            self.replace_numbers()
            self.replace_continuous_punctuation()
            self.replace_periods_before_numeric_references()
            self.text = Text(self.text).apply(
                self.lang.Abbreviation.WithMultiplePeriodsAndEmailRule,
                self.lang.GeoLocationRule, self.lang.FileFormatRule)
            postprocessed_sents = self.split_into_segments()
            return postprocessed_sents

        def replace_numbers(self):
            self.text = Text(self.text).apply(*self.lang.Numbers.All)
            self.replace_period_in_ordinal_numerals()
            self.replace_period_in_roman_numerals()
            return self.text

        def replace_period_in_ordinal_numerals(self):#TODO review usage and instance
            # Rubular: https://rubular.com/r/0HkmvzMGTqgWs6
            self.text = re.sub(r'(?<=\d)\.(?=\s*[a-z]+)', '∯', self.text)

        def replace_period_in_roman_numerals(self):#TODO review usage and instance
            # Rubular: https://rubular.com/r/XlzTIi7aBRThSl
            self.text = re.sub(r'(((?<=^)|(?<=\A)|(?<=\s))[vxi]+)(\.)( )(–)(?=\s+)', r'\1∯', self.text, flags=re.IGNORECASE)
            "((\s+[VXI]+) | (^[VXI]+))(\.)(?=\s+)"

            self.text = re.sub(r'((?<=^)|(?<=\A)|(?<=\s))([ivxIVX]+)(\. –)', r'\1\2∯', self.text, flags=re.IGNORECASE)