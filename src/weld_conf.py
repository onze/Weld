
################################debug purposes
debug = True


################################general weld

#path to resources that can be loaded by steel
weld_data_path = 'data'

#ogre resource group of internal 3d models
weld_resource_group='weld_internals'

#name of the folder where useless files are moved to
weld_trash_folder='trash'

###############################resources browser
#files dragged from weld resource browser can have a list of other files they
#depend on. this dictionary lists them.
res_dep = {
            'mesh':['mesh', 'material', 'png'],
        }

#this dict tells in what folder to find files, given their extension.
resource_ext_to_dirs = {
    'mesh':'meshes',
    'material':'materials',
    'png':'materials',
}


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

