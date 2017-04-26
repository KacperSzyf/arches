'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from django.conf import LazySettings
from arches.app.models import models


class SystemSettings(LazySettings):
    """
    This class can be used just like you would use settings.py 

    To use, import like you would the django settings module:
        
        from system_settings import settings
        ....
        settings.SEARCH_ITEMS_PER_PAGE 

        # will list all settings
        print settings

    """

    graph_id = 'ff623370-fa12-11e6-b98b-6c4008b05c4c'
    resourceinstanceid = 'a106c400-260c-11e7-a604-14109fd34195'
    settings = {} # includes all settings including methods and private attributes defined in settings.py

    def __init__(self, *args, **kwargs):
        super(SystemSettings, self).__init__(*args, **kwargs)
        try: 
            self.update_settings()
        except:
            pass
        #print self

    def __str__(self):
        ret = []
        for setting in dir(self):
            if setting.isupper():
                setting_value = getattr(self, setting)
                ret.append("%s = %s" % (setting, setting_value))
        return '\n'.join(ret)

    def get(self, setting_name):
        """
        Used to retrieve any setting, even callable methods defined in settings.py

        """

        return self.settings[setting_name]

    def update_settings(self):
        """
        Updates the settings the Arches System Settings graph

        """

        # get all the possible settings defined by the Arches System Settings Graph
        for node in models.Node.objects.filter(graph_id=self.graph_id):
            # if node.datatype != 'semantic':
            #     self.settings[node.name] = None
            #     setattr(self, node.name, None)
            def setup_node(node, parent_node=None):
                if node.is_collector:
                    if node.nodegroup.cardinality == '1':
                        obj = {}
                        for decendant_node in self.get_direct_decendent_nodes(node):
                            # setup_node(decendant_node)
                            # if decendant_node.name not in self.settings:
                            #     self.settings[decendant_node.name] = None
                            #     setattr(self, decendant_node.name, None)
                            obj[decendant_node.name] = setup_node(decendant_node, node)

                        self.settings[node.name] = obj
                        #setattr(self, node.name, obj)

                    if node.nodegroup.cardinality == 'n':
                        self.settings[node.name] = []
                        #setattr(self, node.name, [])
                    return self.settings[node.name]

                if parent_node is not None:
                    self.settings[node.name] = None
                    #setattr(self, node.name, None)

            setup_node(node)

        # set any values saved in the instance of the Arches System Settings Graph 
        for tile in models.TileModel.objects.filter(resourceinstance__graph_id=self.graph_id):
            if tile.nodegroup.cardinality == '1':
                for node in tile.nodegroup.node_set.all():
                    if node.datatype != 'semantic':
                        try:
                            val = tile.data[str(node.nodeid)]
                            self.settings[node.name] = val
                            #setattr(self, node.name, val)
                        except:
                            pass

            if tile.nodegroup.cardinality == 'n':
                obj = {}
                collector_nodename = ''
                for node in tile.nodegroup.node_set.all():
                    # print "%s: %s" % (node.name,node.is_collector)
                    if node.is_collector:
                        collector_nodename = node.name
                    if node.datatype != 'semantic':
                        obj[node.name] = tile.data[str(node.nodeid)]
                    # try:
                    #     #val = tile.data[str(node.nodeid)]
                    #     obj[node.name] = tile.data[str(node.nodeid)]
                    #     # self.settings[node.name] = val
                    #     # setattr(self, node.name, val)
                    # except:
                    #     pass

                # print collector_nodename
                # print obj

                self.settings[collector_nodename].append(obj)
                #setattr(self, collector_nodename, ret)

        for setting_name, setting_value in self.settings.iteritems():
            if setting_name.isupper():
            #if not setting_name.startswith('__') and not callable(self.settings[setting_name]):
                setattr(self, setting_name, setting_value)

        print self


    @classmethod
    def get_direct_decendent_nodes(cls, node):
        nodes = []
        for edge in models.Edge.objects.filter(domainnode=node):
            nodes.append(edge.rangenode)
        return nodes


settings = SystemSettings()