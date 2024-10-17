
enumDict = {
	'gnc_sru_asleep_no_asleep':[
			'ASLEEP',
			'NO_ASLEEP',
			],
	'gnc_sru_cmd_arg_en_dis':[
			'DISABLED',
			'ENABLED',
			],
	'gnc_sru_config':[
			'HYRDA',
			'EUROPA',
			],
	'gnc_sru_mgr_photo_buffer':[
			'PHOTO_BUFFER_0',
			'PHOTO_BUFFER_1',
			'PHOTO_BUFFER_2',
			'PHOTO_BUFFER_3',
			],
	'gnc_sru_mram_scanning_flag':[
			'NO_SCANNING',
			'SCANNING',
			],
	'gnc_sru_op_code':[
			'SWITCH_OFF_OH',
			'SWITCH_ON_OH',
			'ENABLE_OH_NO_QTRN',
			'ENABLE_OH_FOR_QTRN',
			'ACTIVATE_INTER_HEADS_CAL',
			'DEACTIVATE_INTER_HEADS_CAL',
			'SWITCH_REDUND_OH',
			],
	'gnc_sru_self_test':[
			'TC_MEMORY',
			'TM_MEMORY',
			'1553_MEMORY',
			'OH1_MEMORY_FULL',
			'OH1_MEMORY_HALF',
			'OH2_MEMORY_FULL',
			'OH2_MEMORY_HALF',
			'RESOURCE_MEMORY',
			'LOG1_MEMORY',
			'LOG2_MEMORY',
			'LOG3_MEMORY',
			'DMA_MEMORY',
			],
	'gnc_which_sru_eu':[
			'SRU_EU_A',
			'SRU_EU_B',
			'PRIME_SRU_EU',
			'NON_PRIME_SRU_EU',
			],
	'gnc_which_sru_oh':[
			'BOTH',
			'SRU_OH_1',
			'SRU_OH_2',
			'SRU_OH_FOR_CTRL',
			],
	'sru_mem_loc':[
			'RAM',
			'MRAM_0',
			'MRAM_1',
			],
}

cmdDict = {
	'GNC_SRU_EU_POWER_ON':{
		'opcode':'0xFDDA',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_EU_POWER_OFF':{
		'opcode':'0xFDDB',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_SET_STANDBY':{
		'opcode':'0xFDDF',
		'args': [
			{'name':'gnc_which_sru','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_SET_ATT_TRACK':{
		'opcode':'0xFDE0',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_qrspre_1','type':'float_arg','length':64,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_2','type':'float_arg','length':64,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_3','type':'float_arg','length':64,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_4','type':'float_arg','length':64,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_wxrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wyrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wzrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_date','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'gnc_sru_date_val_tc','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_UPDATE_ANG_RATE':{
		'opcode':'0xFDE5',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_ang_rate_assist','type':'gnc_sru_cmd_arg_en_dis','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_wxrs','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wyrs','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wzrs','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_date_val_w','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_UPDATE_ACQUISITION':{
		'opcode':'0xFDE6',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_configuration','type':'gnc_sru_config','length':16,'range_min':None,'range_max':None},
			{'name':'gnc_sru_integration_time','type':'unsigned_arg','length':16,'range_min':1,'range_max':80},
			{'name':'gnc_sru_star_select_threshold','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_UPDATE_TRACKING':{
		'opcode':'0xFDE7',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_number_subimages','type':'integer_arg','length':16,'range_min':1,'range_max':15},

		      ]
		},
	'GNC_SRU_TRIGGER_ACQUISITION':{
		'opcode':'0xFDE8',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_SET_EXT_OH_REF_FRAME':{
		'opcode':'0xFDE9',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_CONFIG_OH':{
		'opcode':'0xFDEA',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_oh_configuration','type':'gnc_sru_op_code','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_SET_AOM':{
		'opcode':'0xFDEB',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_qrspre_1','type':'float_arg','length':32,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_2','type':'float_arg','length':32,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_3','type':'float_arg','length':32,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_qrspre_4','type':'float_arg','length':32,'range_min':-1,'range_max':1},
			{'name':'gnc_sru_wxrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wyrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_wzrspre','type':'float_arg','length':32,'range_min':-2,'range_max':2},
			{'name':'gnc_sru_date','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'gnc_sru_date_val_qtrn_tc','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'gnc_sru_desig_accuracy_ang_vel_1','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},
			{'name':'gnc_sru_desig_accuracy_ang_vel_2','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},
			{'name':'gnc_sru_desig_accuracy_ang_vel_3','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},
			{'name':'gnc_sru_date_val_w_pre','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_RESET':{
		'opcode':'0xFDEC',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_DO_SELF_TEST':{
		'opcode':'0xFDED',
		'args': [
			{'name':'gnc_which_sru','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_self_test','type':'gnc_sru_self_test','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_TAKE_PHOTO':{
		'opcode':'0xFEA5',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_which_oh','type':'gnc_which_sru_oh','length':16,'range_min':None,'range_max':None},
			{'name':'gnc_sru_integration_time','type':'unsigned_arg','length':16,'range_min':1,'range_max':8000},
			{'name':'gnc_sru_xraps','type':'unsigned_arg','length':16,'range_min':0,'range_max':1021},
			{'name':'gnc_sru_yraps','type':'unsigned_arg','length':16,'range_min':1,'range_max':1022},
			{'name':'gnc_sru_dim_xraps','type':'unsigned_arg','length':16,'range_min':3,'range_max':1024},
			{'name':'gnc_sru_dim_yraps','type':'unsigned_arg','length':16,'range_min':1,'range_max':1022},
			{'name':'which_buffer_to_collect_to','type':'gnc_sru_mgr_photo_buffer','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_READ_MEMORY':{
		'opcode':'0xFEA6',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'gnc_sru_mem_address','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'gnc_sru_mem_length','type':'unsigned_arg','length':16,'range_min':1,'range_max':476},

		      ]
		},
	'GNC_SRU_POWER_ON_OH':{
		'opcode':'0xFF28',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_ENTER_TRACK_BEHAVIOR':{
		'opcode':'0xFF30',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_POWER_OFF_OH':{
		'opcode':'0xFF57',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_READ_DIAG_DATA':{
		'opcode':'0xFF81',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_ABORT_ACQUISITION_SCHEME':{
		'opcode':'0xFF82',
		'args': []
		},
	'GNC_SRU_ENABLE_SECOND_OH':{
		'opcode':'0xFF83',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'which_sru_oh','type':'gnc_which_sru_oh','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_DMP_SRU_PHOTO_DATA':{
		'opcode':'0xFFA3',
		'args': [
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':0,'range_max':100},
			{'name':'which_buffer','type':'gnc_sru_mgr_photo_buffer','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_LOAD_APP_SW':{
		'opcode':'0xFFA4',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'mem_loc','type':'sru_mem_loc','length':8,'range_min':None,'range_max':None},
			{'name':'mem_address','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'file_path','type':'var_string_arg','length':1024,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_ASLEEP_NO_ASLEEP_MRAM':{
		'opcode':'0xFFA8',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},
			{'name':'cmd_type_on_sru_mram','type':'gnc_sru_asleep_no_asleep','length':16,'range_min':None,'range_max':None},
			{'name':'sru_mram_scanning_flag','type':'gnc_sru_mram_scanning_flag','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'GNC_SRU_ABORT_TAKE_PHOTO_BEHAVIOR':{
		'opcode':'0xFFAC',
		'args': []
		},
	'GNC_SRU_ABORT_LOAD_APP_SW':{
		'opcode':'0xFFC1',
		'args': []
		},
	'GNC_SRU_UPDATE_JULIAN_DATE':{
		'opcode':'0xFFCB',
		'args': [
			{'name':'which_sru_eu','type':'gnc_which_sru_eu','length':8,'range_min':None,'range_max':None},

		      ]
		},
}
