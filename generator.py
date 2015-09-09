#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json


class Attribute(object):
    """Stores an indexes of an attribute used in lists of readers and dates."""
    # List.list
    name = 0
    lection = 1
    psalm = 2
    believers_pray = 3
    speech_number = 4

    # dates_and_hours
    date = 0
    is_second_lection = 1
    hours = 2


class List(object):
    """
    List of available people and their lection preferences. Each person has 3 fields describing state of relation
    towards a lection and speech_number used to sorting before new reading list generation.
    """

    def __init__(self) -> None:
        """Init an list with readers and generator's vars."""
        self.list_ = []
        self.html_file = ''
        self.load_list()

    def load_list(self):
        """Loads data from 'list.json' and place it into 'self.list_'."""
        try:
            with open("list.json", 'r') as file:
                self.list_ = json.loads(file.read())
        except FileNotFoundError:
            pass

    def add_new_person(self, name, lection, psalm, believers_pray) -> bool:
        """Add new person at the end of self.list_ and update 'list.json'."""
        name_validity = isinstance(name, str)
        lection_validity = isinstance(lection, bool)
        psalm_validity = isinstance(psalm, bool)
        believers_pray_validity = isinstance(believers_pray, bool)

        if name_validity and lection_validity and psalm_validity and believers_pray_validity:
            self.list_.append([name, lection, psalm, believers_pray, 0])
            self.json_file_update()
            return True
        else:
            return False

    def delete_person(self, name) -> bool:
        """
        Removes person from the list.
        Handling situation when exist more than one the same names is unnecessary - it doesn't have an influence
        for second person.
        """
        for i in range(len(self.list_)):
            if name in self.list_[i]:
                del self.list_[i]
                self.json_file_update()
                return True

        return False

    def json_file_update(self) -> bool:
        """Override file list.json with new self.list_."""
        with open("list.json", 'w') as file:
            file.write(json.dumps(self.list_))

        return True

    # html list generating methods
    def sort_by_speeches(self):
        """Sorts self.list_ by number of speeches."""
        self.list_.sort(key=lambda person: person[Attribute.speech_number])

    def get_reader(self, lection_type) -> str:
        """Return name of person whose speech_number is smallest and his relation towards lection 'type' is True.
        :rtype:str
        """
        self.sort_by_speeches()
        for person in self.list_:
            if person[lection_type]:
                person[Attribute.speech_number] += 1
                return person[Attribute.name]

    def create_html_readers_list(self, days_hours) -> bool:
        """
        Creates html file with list of readers.

        :param days_hours: structure: [["date1", if_second_lection, ["hour1", "hour2"]], (...),
        ["date_n", if_second_lection, ["hour1", (...), "hour_n"]]
        :return: True if successful, False if invalid input.
        """
        self.html_file = ('<!DOCTYPE html>\n'
                          '<html>\n'
                          '<head>\n'
                          '<meta charset=\"UTF-8\">\n'
                          '<style>\n'
                          'h1 {{\n'
                          '    text-align: center;\n'
                          '}}\n'
                          'table, th, td {{\n'
                          '    border: 1px solid black;\n'
                          '    border-collapse: collapse;\n'
                          '}}\n'
                          'th, td {{\n'
                          '    text-align: center;\n'
                          '}}\n'
                          '</style>\n'
                          '</head>\n'
                          '<body>\n'
                          '<h1>Lista czytających: {first} - {last}</h1>\n').format(first=days_hours[0][Attribute.date],
                                                                                   last=days_hours[-1][Attribute.date])

        self.html_file = ('{head}<table>\n'
                          '<tr>\n'
                          ' <th>Data</th>\n'
                          ' <th>Godzina</th>\n'
                          ' <th>I czytanie</th>\n'
                          ' <th>II czytanie</th>\n'
                          ' <th>Psalm</th>\n'
                          ' <th>Modlitwa wiernych</th>\n'
                          '</tr>\n').format(head=self.html_file)

        # main block of generator
        for date in days_hours:
            self.html_file = '{head}<tr>\n'.format(head=self.html_file)

            # span the same number of rows as date[Attribute.hours] has various hours
            self.html_file = '{head}<th rowspan="{no_hours}">{date}</th>\n'.format(head=self.html_file,
                                                                                   no_hours=len(date[Attribute.hours]),
                                                                                   date=date[Attribute.date])

            # first hour has to be written manually because of started <tr>
            first_lection = self.get_reader(Attribute.lection)

            # if second lection will be read
            if date[Attribute.is_second_lection]:
                second_lection = self.get_reader(Attribute.lection)
            else:
                second_lection = '-'

            psalm = self.get_reader(Attribute.psalm)
            believers_pray = self.get_reader(Attribute.believers_pray)

            self.html_file = ('{head}<th>{hour}</th>\n'
                              ' <td>{lct_1}</td>\n'
                              ' <td>{lct_2}</td>\n'
                              ' <td>{ps}</td>\n'
                              ' <td>{pray}</td>\n'
                              '</tr>\n').format(head=self.html_file, hour=date[Attribute.hours][0],
                                                lct_1=first_lection, lct_2=second_lection, ps=psalm,
                                                pray=believers_pray)

            for i in range(1, len(date[Attribute.hours])):
                first_lection = self.get_reader(Attribute.lection)

                # if second lection will be read
                if date[Attribute.is_second_lection]:
                    second_lection = self.get_reader(Attribute.lection)
                else:
                    second_lection = '-'

                psalm = self.get_reader(Attribute.psalm)
                believers_pray = self.get_reader(Attribute.believers_pray)

                self.html_file = ('{head}<tr>\n'
                                  ' <th>{hour}</th>\n'
                                  ' <td>{lct_1}</td>\n'
                                  ' <td>{lct_2}</td>\n'
                                  ' <td>{ps}</td>\n'
                                  ' <td>{pray}</td>\n'
                                  '</tr>\n').format(head=self.html_file, hour=date[Attribute.hours][i],
                                                    lct_1=first_lection, lct_2=second_lection, ps=psalm,
                                                    pray=believers_pray)

        self.html_file = ('{head}</table>\n'
                          '</body>\n'
                          '</html>').format(head=self.html_file)

        first_date_html_file = '{first} - {last}'.format(first=days_hours[0][Attribute.date][0:5],
                                                         last=days_hours[-1][Attribute.date][0:5])

        first_date_html_file = '{head}.html'.format(head=first_date_html_file)
        with open(first_date_html_file, 'w') as file:
            file.write(self.html_file)

        return True
