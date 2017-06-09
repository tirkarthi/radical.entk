__copyright__   = "Copyright 2017-2018, http://radical.rutgers.edu"
__author__      = "Vivek Balasubramanian <vivek.balasubramaniana@rutgers.edu>"
__license__     = "MIT"

import radical.utils as ru
from radical.entk.exceptions import *
import radical.pilot as rp
import os

class ResourceManager(object):

    def __init__(self, resource_desc):

        self._logger = ru.get_logger('radical.entk.resource_manager')

        self._logger.info('Resource Manager initialized')

        self._session = None    
        self._pmgr = None
        self._pilot = None
        self._resource_desc = None

        self._logger.debug('Validating resource description')
        if self._validate_resource_desc(resource_desc):
            self._resource_desc = resource_desc
            self._logger.info('Resource description validated')
            self._logger.debug('Populating resource manager object')
            self._populate(resource_desc)
        else:
            self._logger.error('Could not validate resource description')
            raise


        self._mlab_url = os.environ.get('RADICAL_PILOT_DBURL',None)
        if not self._mlab_url:
            raise Error(text='RADICAL_PILOT_DBURL not defined. Please assign a valid mlab url')    

    #----------------------------------------------------------------------------------------------------
    # Getter methods

    @property
    def pilot(self):

        """
        :getter: Return reference to the submitted Pilot
        """
        return self._pilot

    @property
    def session(self):

        """
        :getter: Return reference to the Radical Pilot session instance currently being used
        """
        return self._session

    @property
    def pmgr(self):

        """
        :getter: Return reference to the Radical Pilot manager currently being used
        """
        return self._pmgr

    @property
    def resource_desc(self):
        return self._resource_desc
    #----------------------------------------------------------------------------------------------------

    def _validate_resource_desc(self, resource_desc):

        """
        Validate the resource description that was provided to current class's constructor
        """

        try:

            if not isinstance(resource_desc, dict):
                raise TypeError(expected_type=dict, actual_type=type(resource_desc))


            expected_keys = [   'resource',
                                'walltime',
                                'cores',
                                'project'
                            ]

            for key in expected_keys:
                if key not in resource_desc:
                    raise Error(text='Key %s does not exist in the resource description'%key)

            return True

        except Exception, ex:
            self._logger.error('Failed to validate resource description')
            raise

    def _populate(self, resource_desc):

        """
        Populate the class attributes with values provided in the resource description
        """

        try:

            self._resource = resource_desc['resource']
            self._walltime = resource_desc['walltime']
            self._cores = resource_desc['cores']
            self._project = resource_desc['project']

            if 'access_schema' in resource_desc:
                self._access_schema = resource_desc['access_schema']
            else:
                self._access_schema = None
        
            if 'queue' in resource_desc:
                self._queue = resource_desc['queue']
            else:
                self._queue = None

            self._logger.debug('Resource manager population successful')

        except Exception, ex:
            self._logger.error('Resource manager population unsuccessful')
            raise


    def submit_resource_request(self):

        """
        Function to initiate the resource request
        Currently, submits a Pilot job using the RADICAL Pilot system
        """

        try:

            def _pilot_state_cb(pilot, state):
                self._logger.info('Pilot %s state: %s'%(pilot.uid, state))

                if state == rp.FAILED:
                    self._logger.error('Pilot has failed')
                    raise

            self._session = rp.Session(dburl=self._mlab_url)

            self._pmgr = rp.PilotManager(session=self._session)
            self._pmgr.register_callback(_pilot_state_cb)

            pd_init = {
                    'resource'  : self._resource,
                    'runtime'   : self._walltime,
                    'cores'     : self._cores,
                    'project'   : self._project,
                    }
    
            if self._access_schema:
                pd_init['access_schema'] = self._access_schema
    
            if self._queue:
                pd_init['queue'] = self._queue
    

            pdesc = rp.ComputePilotDescription(pd_init)
    
            # Launch the pilot
            self._pilot = self._pmgr.submit_pilots(pdesc)

            self._logger.info('Resource request submission successful.. waiting for pilot to go Active')
    
            # Wait for pilot to go active
            self._pilot.wait(rp.ACTIVE) 

            self._logger.info('Pilot is now active')

        except Exception, ex:
            self._logger.error('Resource request submission failed, error: %s'%ex)
            raise