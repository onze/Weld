
################################debug purposes
debug = True


################################general weld

#path to resources that can be loaded by steel
weld_data_path = 'data'

#root folder for behavior trees
weld_BT_root_folder = 'BT'

#ogre resource group of internal 3d models
weld_resource_group = 'weld_internals'

#name of the folder where useless files are moved to
weld_trash_folder = 'trash'

################################BTrees

# Those are classes Steel knows about.
BT_nodes_classes_names = [
    'BTSequence',
    'BTSelector',
    'BTTimeFilter',
    'BTLocalizer',
    'BTNavigator',
    'BTSensor',
    'BTTagEditor',
    'BTOgreModelAnimator',
    'BTDecorator_NOT',
]

#If set to True, during BT export, weld will print a warning message for each
#file in a BT subdirectory that does not satisfy info_file criteria:
#   - its name does not start with 2 underscores
#   - its name is not one listed in BT_nodes_classes_names or BT_leaves_classes_names.
BT_warn_for_unexpected_infofiles = False

# include extra info in BT serialized nodes, like the file they've been serialized
# from, etc.
# Attributes added because of this flag start with '__'.
BT_serialization_add_debug_info = False

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

# show steel/ogre init
show_ogre_init = False

# TODO: camera speed, as a tuple (dx,dy,dz)
# camera_speed=()

# distance from cam at which a dropped object is instanciated, as a tuple (dx,dy,dz)
drop_target_vec = (.0, -1., -10.)

################################projects
# data path within project root folder
project_data_path = 'data'
on_weld_start_reopen_last_project = True

################################levels
on_project_opening_reopen_last_level = True

