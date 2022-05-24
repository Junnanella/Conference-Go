from json import JSONEncoder
from datetime import datetime


class DateEncoder(JSONEncoder):
    def default(self, o):
        # if o is an instance of datetime
        if isinstance(o, datetime):
            #    return o.isoformat()
            return o.isoformat()
        # otherwise
        else:
            #    return super().default(o)
            return super().default(o)


class ModelEncoder(DateEncoder, JSONEncoder):
    def default(self, object):
        #   if the object to decode is the same class as what's in the
        #   model property, then
        if isinstance(object, self.model):
            #     * create an empty dictionary that will hold the property
            #       names
            #       as keys and the property values as values
            d = {}
            #     * for each name in the properties list
            for property in self.properties:
                #      * get the value of that property from the model instance
                #        given just the property name
                #       * put it into the dictionary with that property name as
                #        the key
                d[property] = getattr(object, property)
            #     * return the dictionary
            return d
        #   otherwise,
        #       return super().default(o)  # From the documentation
        else:
            return super().default(object)
