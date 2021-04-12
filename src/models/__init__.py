from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import Model
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func, desc

import inspect                                                              
import pkgutil                                                                 
import importlib                                                               
import sys 

bcrypt = Bcrypt()

db = SQLAlchemy()

__all__ = ['association_tables', 'role', 'user', 'thread', 'topic', 'post', 'chat', 'message', 'topictag']

def import_models():                                                           
    thismodule = sys.modules[__name__]                                         

    for loader, module_name, is_pkg in pkgutil.iter_modules(                   
            thismodule.__path__, thismodule.__name__ + '.'):                   
        module = importlib.import_module(module_name, loader.path)             
        for name, _object in inspect.getmembers(module, inspect.isclass):      
            globals()[name] = _object                                                                                 

import_models()