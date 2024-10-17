
enumDict = {
	'dpm_svc_sent_status':[
			'SENT',
			'UNSENT',
			'ALL',
			],
	'dpm_svc_time_type':[
			'DVT',
			'CREATION_TIME',
			],
	'enable_disable':[
			'DISABLE',
			'ENABLE',
			],
}

cmdDict = {
	'DDM_SHOW_DP_INFO':{
		'opcode':'0xFBA3',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'creation_time_seconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'creation_time_subseconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},

		      ]
		},
	'DDM_DEL_DP_IND':{
		'opcode':'0xFBCF',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'creation_time_seconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'creation_time_subseconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},

		      ]
		},
	'DDM_ASSERT_DP_AUTO_COMPRESSION':{
		'opcode':'0xFBD3',
		'args': [
			{'name':'enable_disable','type':'enable_disable','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'DDM_DMP_DATA_CATALOG':{
		'opcode':'0xFC00',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':0,'range_max':2039},
			{'name':'filter_time_type','type':'dpm_svc_time_type','length':8,'range_min':None,'range_max':None},
			{'name':'filter_time_start','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'filter_time_end','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'filter_sent_status','type':'dpm_svc_sent_status','length':8,'range_min':None,'range_max':None},
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':0,'range_max':100},

		      ]
		},
	'DDM_DEL_DP':{
		'opcode':'0xFC01',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':0,'range_max':2039},
			{'name':'time_type','type':'dpm_svc_time_type','length':8,'range_min':None,'range_max':None},
			{'name':'filter_time_start','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'filter_time_end','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'sent_status','type':'dpm_svc_sent_status','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'DDM_COMPRESS_DP':{
		'opcode':'0xFC02',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'creation_time_start_seconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'creation_time_start_subseconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'creation_time_end_seconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'creation_time_end_subseconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'DDM_UPDATE_DP_DWN_PRIORITY':{
		'opcode':'0xFC04',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':0,'range_max':2039},
			{'name':'time_type','type':'dpm_svc_time_type','length':8,'range_min':None,'range_max':None},
			{'name':'filter_time_start','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'filter_time_end','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':1,'range_max':100},

		      ]
		},
	'DDM_RETRANSMIT_DP':{
		'opcode':'0xFC05',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'creation_time_seconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'creation_time_subseconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'dp_part_range_start','type':'unsigned_arg','length':16,'range_min':0,'range_max':2519},
			{'name':'dp_part_range_end','type':'unsigned_arg','length':16,'range_min':0,'range_max':2519},

		      ]
		},
	'DDM_UPDATE_DP_DWN_PRIORITY_IND':{
		'opcode':'0xFC06',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'creation_time_seconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'creation_time_subseconds','type':'unsigned_arg','length':32,'range_min':0,'range_max':4294967295},
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':1,'range_max':100},

		      ]
		},
	'DDM_SYNC_LINKED_DP':{
		'opcode':'0xFC09',
		'args': []
		},
	'DDM_LOAD_DP_CONFIG_TBL':{
		'opcode':'0xFC0A',
		'args': [
			{'name':'filename','type':'var_string_arg','length':1024,'range_min':None,'range_max':None},

		      ]
		},
	'DDM_MOVE_INST_DP':{
		'opcode':'0xFC1E',
		'args': [
			{'name':'apid','type':'unsigned_arg','length':16,'range_min':1,'range_max':2039},
			{'name':'dvt_or_creation_time','type':'dpm_svc_time_type','length':8,'range_min':None,'range_max':None},
			{'name':'time_start_seconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'time_start_subseconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'time_end_seconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'time_end_subseconds','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'DDM_DMP_ACTIVE_DPCT':{
		'opcode':'0xFF1D',
		'args': [
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':0,'range_max':100},

		      ]
		},
}
