
################################debug purposes
debug = True


################################general weld

#path to resources that can be loaded by steel
weld_data_path = 'data'

resource_ext_to_dirs = {
    'mesh':'meshes',
    'material':'materials'
}

#ogre resource group of internal 3d models
weld_resource_group='weld_internals'

###############################resources browser


###############################qsteelwidget

#show steel/ogre init
show_ogre_init = False

#TODO: camera speed, as a tuple (dx,dy,dz)
#camera_speed=()

#distance from cam at which a dropped object is instanciated, as a tuple (dx,dy,dz)
drop_target_vec = (.0, -1., -10.)

################################projects
#data path within project root folder
project_data_path = 'data'
on_open_reopen_last_project = 1

