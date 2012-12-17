from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.savedargparse import SavedArgumentParser as ArgumentParser
from ast import literal_eval
from core.utils import join_abs_paths
import os


class Systemfiles(ModuleProbe):
    '''Enumerate system files permissions'''

    def _set_vectors(self):
        self.support_vectors.add_vector('find', 'find.name', ["$path", "$mode", "-no-recursion", "$recurs"])
        self.support_vectors.add_vector('users', 'audit.etcpasswd', ["-real"])
    
    def _set_args(self):
        self.argparser.add_argument('-etc-writable', action='store_false', default=True)
        self.argparser.add_argument('-spool-cron-writable', action='store_false', default=True)
        self.argparser.add_argument('-homes', action='store_false', default=True)
        self.argparser.add_argument('-logs', action='store_false', default=True)
        self.argparser.add_argument('-binaries', action='store_false', default=True)

    def __etc_writable(self):
        result = self.support_vectors.get('find').execute({'path' : '/etc/', 'mode' : '-writable', 'recurs' : True })   
        self.mprint('Writable files in \'/etc/\' and subfolders ..')
        if result: 
            self.mprint('\n%s' % '\n'.join(result))     
            return {'etc_writable' : result }
        else:
            return {}
        
    def __cron_writable(self):
        result = self.support_vectors.get('find').execute({'path' : '/var/spool/cron/', 'mode' : '-writable', 'recurs' : True })   
        self.mprint('Writable files in \'/var/spool/cron\' and subfolders ..')
        if result: 
            self.mprint('\n%s' % '\n'.join(result))     
            return { 'cron_writable' : result }
        else:
            return {}
        
    def __homes(self):
        dict_result = {}
        
        result = self.support_vectors.get('find').execute({'path' : '/home/', 'mode' : '-writable', 'recurs': False })  
        self.mprint('Writable folders in \'/home/\' ..')
        if result: 
            self.mprint('\n%s' % '\n'.join(result))  
            dict_result.update({'home_writable': result })
            
        result = self.support_vectors.get('find').execute({'path' : '/home/', 'mode' : '-executable', 'recurs': False })   
        self.mprint('Browsable folders in \'/home/\' ..')
        if result: 
            self.mprint('\n%s' % '\n'.join(result))  
            dict_result.update({'home_executable': result })
        
        result = self.support_vectors.get('find').execute({'path' : '/', 'mode' : '-writable', 'recurs': False })   
        self.mprint('Writable folders in \'/\' ..')
        if result: 
            self.mprint('\n%s' % '\n'.join(result))  
            dict_result.update({'root_executable': result })
        
        return dict_result
        
    def __logs(self):
        result = self.support_vectors.get('find').execute({'path' : '/var/log/', 'mode' : '-readable', 'recurs': True })   
        self.mprint('Readable files in \'/var/log/\' and subfolders ..')

        if result: 
            self.mprint('\n%s' % '\n'.join(result))     
            return { 'log_writable' : result }
        else:
            return {}

    def __bins(self):
        
        dict_result = {}
        paths = ['/bin/', '/usr/bin/', '/usr/sbin', '/sbin', '/usr/local/bin', '/usr/local/sbin']
        
        for path in paths:
            result = self.support_vectors.get('find').execute({'path' : path, 'mode' : '-writable', 'recurs': True })   
            self.mprint('Writable files in \'%s\' and subfolders ..' % path)
            if result: 
                self.mprint('\n%s' % '\n'.join(result))  
                dict_result.update({ '%s_writable' % path : result })
                
        return dict_result
            
    def _probe(self):
        
        self._result = {}
        
        if self.args['etc_writable']:
            self._result.update(self.__etc_writable())
        
        if self.args['spool_cron_writable']:
            self._result.update(self.__cron_writable())    

        if self.args['homes']:
            self._result.update(self.__homes())
            
        if self.args['logs']:
            self._result.update(self.__logs())        
            
        if self.args['binaries']:
            self._result.update(self.__bins())              
               
   
    def _output_result(self):
       pass
                        