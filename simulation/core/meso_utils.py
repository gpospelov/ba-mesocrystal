"""
Collection of various utils for meso simulation.
"""
import os
import json
import sys
import numpy.random as npr


def load_setup(json_filename, config_name=None):
    """
    Loads json description from given filename corresponding to given config_name
    """
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", json_filename)
    print("{0}".format('-'*80))
    print("'{0}' ==> '{1}'".format(json_filename, config_name))
    print("{0}".format('-'*80))
    with open(filename) as json_file:
        data = json.load(json_file)
        if config_name:
            return data[config_name]
        else:
            return data


def create_object(class_key, config):
    class_name = config[class_key]
    return globals()[class_name](config)


def random_gate(a, b):
    return a + (b-a)*npr.random()
