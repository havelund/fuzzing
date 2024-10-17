
enumDict = {
	'uvs_actuator_select':[
			'DET_DOOR_PRI',
			'DET_DOOR_RED',
			'DET_DOOR_BOTH',
			'AP_UNLATCH_PRI',
			'AP_UNLATCH_RED',
			'HP_UNLATCH_PRI',
			'HP_UNLATCH_RED',
			'SP_OPEN_PRI',
			'SP_OPEN_RED',
			'SP_CLOSE_PRI',
			'SP_CLOSE_RED',
			'NONE_STOP',
			],
	'uvs_close_open':[
			'CLOSED',
			'OPEN',
			],
	'uvs_counter_id':[
			'REJECT_COUNTER',
			'EXECUTED_COUNTER',
			'ACCEPT_COUNTER',
			'SPW_ERRORS_COUNTER',
			],
	'uvs_critical_confirm':[
			'UVS_CMD_DOOR',
			'UVS_SET_PARAM',
			'UVS_STORE_PARAMS_NV',
			'UVS_START_HIST_ACQ',
			'UVS_START_PIX_ACQ',
			'UVS_START_HV_RAMP',
			'UVS_ACTIVATE_ACTUATOR',
			'UVS_STORE_LUT_NV',
			'UVS_MEMORY_LOAD',
			'UVS_START_PROGRAM',
			'UVS_TEST_PANIC',
			],
	'uvs_door_state':[
			'SAME',
			'OPEN',
			'CLOSED',
			],
	'uvs_enable_disable':[
			'DISABLE',
			'ENABLE',
			],
	'uvs_lut':[
			'SPECTRAL',
			'SPATIAL',
			'PULSEHEIGHT',
			],
	'uvs_lut_load':[
			'LINEAR',
			'LUT_NVRAM_01',
			'LUT_NVRAM_02',
			'LUT_NVRAM_03',
			'LUT_NVRAM_04',
			'LUT_NVRAM_05',
			'LUT_NVRAM_06',
			'LUT_NVRAM_07',
			'LUT_NVRAM_08',
			'LUT_NVRAM_09',
			'LUT_NVRAM_10',
			],
	'uvs_lut_select':[
			'TRANSPARENT',
			'LUT_NVRAM_1',
			'LUT_NVRAM_2',
			'LUT_NVRAM_3',
			'LUT_NVRAM_4',
			'LUT_NVRAM_5',
			'LUT_NVRAM_6',
			'LUT_NVRAM_7',
			'LUT_NVRAM_8',
			'LUT_NVRAM_9',
			'LUT_NVRAM_10',
			'ALREADY_LOADED',
			],
	'uvs_lut_set':[
			'LUT_NVRAM_01',
			'LUT_NVRAM_02',
			'LUT_NVRAM_03',
			'LUT_NVRAM_04',
			'LUT_NVRAM_05',
			'LUT_NVRAM_06',
			'LUT_NVRAM_07',
			'LUT_NVRAM_08',
			'LUT_NVRAM_09',
			'LUT_NVRAM_10',
			],
	'uvs_memory_bank':[
			'NVRAM_PAGE_0',
			'NVRAM_PAGE_1',
			'NVRAM_PAGE_2',
			'NVRAM_PAGE_3',
			'NVRAM_PAGE_4',
			'NVRAM_PAGE_5',
			'NVRAM_PAGE_6',
			'NVRAM_PAGE_7',
			'NVRAM_PAGE_8',
			'NVRAM_PAGE_9',
			'NVRAM_PAGE_10',
			'NVRAM_PAGE_11',
			'NVRAM_PAGE_12',
			'NVRAM_PAGE_13',
			'NVRAM_PAGE_14',
			'NVRAM_PAGE_15',
			'ACQMEM',
			'CODE',
			'DATA',
			'RAM',
			],
	'uvs_mode':[
			'UVS_SAFE',
			'UVS_DECON',
			'UVS_CHECKOUT',
			],
	'uvs_overflow_counter':[
			'UVS_CLEAR_COUNTER',
			'UVS_CLEAR_OVERFLOW',
			],
	'uvs_page':[
			'NVRAM_0',
			'NVRAM_1',
			'NVRAM_2',
			'NVRAM_3',
			'PROM',
			'RAM',
			'CURRENT',
			],
	'uvs_param_index':[
			'MODE_CONTROL',
			'MODE_CONTROL_2',
			'SCRUBBERS',
			'HTR_SENSE',
			'HTR_ENABLE',
			'WPA_TIMEOUT',
			'DOOR_SMA_TIME',
			'AP_DOOR_CONTROL',
			'HP_DOOR_CONTROL',
			'SP_DOOR_TIME',
			'CRITICAL_TIMEOUT',
			'TC_MAX_ERROR',
			'HK_RECORD_RATE',
			'REPORT_PARAM',
			'REPORT_SAMPLE',
			'MEM_DUMP_RATE',
			'UVS_TC_LOG_ADDR',
			'HK_NOM_LOG_ADDR',
			'HK_REC_LOG_ADDR',
			'MEM_DMP_LOG_ADDR',
			'HIS_PIX_LOG_ADDR',
			'SCI_CNT_LOG_ADDR',
			'SPARE_BYTE_23',
			'SPARE_BYTE_24',
			'COUNT_RATE_MASK_HI',
			'COUNT_RATE_MAX_LO',
			'SAMPLING_RATE',
			'OFFS_P6P1_VOLT',
			'OFFS_M6P1_VOLT',
			'OFFS_3P3_VOLT',
			'OFFS_1P8_VOLT',
			'OFFS_1P5_VOLT',
			'SPARE_BYTE_33',
			'SPARE_BYTE_34',
			'STIM_ENABLE',
			'HVPS_ENABLE',
			'HV_LEVEL',
			'HV_MAX_HV_SET',
			'HV_STEP_FRACTION',
			'HV_STEP_TIME',
			'HIGH_COUNT_RATE_HI',
			'HIGH_COUNT_RATE_LO',
			'CR_FAIL_HIGH_CNT',
			'HV_BACKOFF_LEVEL_1',
			'HV_BACKOFF_TIMEOUT_1',
			'HV_BACKOFF_LEVEL_2',
			'HV_BACKOFF_TIMEOUT_2',
			'PIXEL_LIST_HACK',
			'PHD_BITS',
			'TEST_FRAME_TIME',
			'DE_TEST_RATE_HI',
			'DE_TEST_RATE_LO',
			'DISCRIM_LOWER',
			'DISCRIM_UPPER',
			'HOT_PIXEL_MASK_0_SPEC_LO',
			'HOT_PIXEL_MASK_0_SPEC_LO_HI',
			'HOT_PIXEL_MASK_0_SPEC_HI',
			'HOT_PIXEL_MASK_0_SPAT_LO',
			'HOT_PIXEL_MASK_0_SPAT_LO_HI',
			'HOT_PIXEL_MASK_0_SPAT_HI',
			'HOT_PIXEL_MASK_1_SPEC_LO',
			'HOT_PIXEL_MASK_1_SPEC_LO_HI',
			'HOT_PIXEL_MASK_1_SPEC_HI',
			'HOT_PIXEL_MASK_1_SPAT_LO',
			'HOT_PIXEL_MASK_1_SPAT_LO_HI',
			'HOT_PIXEL_MASK_1_SPAT_HI',
			'HOT_PIXEL_MASK_2_SPEC_LO',
			'HOT_PIXEL_MASK_2_SPEC_LO_HI',
			'HOT_PIXEL_MASK_2_SPEC_HI',
			'HOT_PIXEL_MASK_2_SPAT_LO',
			'HOT_PIXEL_MASK_2_SPAT_LO_HI',
			'HOT_PIXEL_MASK_2_SPAT_HI',
			'HOT_PIXEL_MASK_3_SPEC_LO',
			'HOT_PIXEL_MASK_3_SPEC_LO_HI',
			'HOT_PIXEL_MASK_3_SPEC_HI',
			'HOT_PIXEL_MASK_3_SPAT_LO',
			'HOT_PIXEL_MASK_3_SPAT_LO_HI',
			'HOT_PIXEL_MASK_3_SPAT_HI',
			'HOT_PIXEL_MASK_4_SPEC_LO',
			'HOT_PIXEL_MASK_4_SPEC_LO_HI',
			'HOT_PIXEL_MASK_4_SPEC_HI',
			'HOT_PIXEL_MASK_4_SPAT_LO',
			'HOT_PIXEL_MASK_4_SPAT_LO_HI',
			'HOT_PIXEL_MASK_4_SPAT_HI',
			'HOT_PIXEL_MASK_5_SPEC_LO',
			'HOT_PIXEL_MASK_5_SPEC_LO_HI',
			'HOT_PIXEL_MASK_5_SPEC_HI',
			'HOT_PIXEL_MASK_5_SPAT_LO',
			'HOT_PIXEL_MASK_5_SPAT_LO_HI',
			'HOT_PIXEL_MASK_5_SPAT_HI',
			'HOT_PIXEL_MASK_6_SPEC_LO',
			'HOT_PIXEL_MASK_6_SPEC_LO_HI',
			'HOT_PIXEL_MASK_6_SPEC_HI',
			'HOT_PIXEL_MASK_6_SPAT_LO',
			'HOT_PIXEL_MASK_6_SPAT_LO_HI',
			'HOT_PIXEL_MASK_6_SPAT_HI',
			'HOT_PIXEL_MASK_7_SPEC_LO',
			'HOT_PIXEL_MASK_7_SPEC_LO_HI',
			'HOT_PIXEL_MASK_7_SPEC_HI',
			'HOT_PIXEL_MASK_7_SPAT_LO',
			'HOT_PIXEL_MASK_7_SPAT_LO_HI',
			'HOT_PIXEL_MASK_7_SPAT_HI',
			'HOT_PIXEL_MASK_8_SPEC_LO',
			'HOT_PIXEL_MASK_8_SPEC_LO_HI',
			'HOT_PIXEL_MASK_8_SPEC_HI',
			'HOT_PIXEL_MASK_8_SPAT_LO',
			'HOT_PIXEL_MASK_8_SPAT_LO_HI',
			'HOT_PIXEL_MASK_8_SPAT_HI',
			'HOT_PIXEL_MASK_9_SPEC_LO',
			'HOT_PIXEL_MASK_9_SPEC_LO_HI',
			'HOT_PIXEL_MASK_9_SPEC_HI',
			'HOT_PIXEL_MASK_9_SPAT_LO',
			'HOT_PIXEL_MASK_9_SPAT_LO_HI',
			'HOT_PIXEL_MASK_9_SPAT_HI',
			'BAND_LIMIT_1_SPEC_LO',
			'BAND_LIMIT_1_SPEC_LO_HI',
			'BAND_LIMIT_1_SPEC_HI',
			'BAND_LIMIT_2_SPEC_LO',
			'BAND_LIMIT_2_SPEC_LO_HI',
			'BAND_LIMIT_2_SPEC_HI',
			'BAND_LIMIT_3_SPEC_LO',
			'BAND_LIMIT_3_SPEC_LO_HI',
			'BAND_LIMIT_3_SPEC_HI',
			'BAND_LIMIT_4_SPEC_LO',
			'BAND_LIMIT_4_SPEC_LO_HI',
			'BAND_LIMIT_4_SPEC_HI',
			'BAND_LIMIT_5_SPEC_LO',
			'BAND_LIMIT_5_SPEC_LO_HI',
			'BAND_LIMIT_5_SPEC_HI',
			'MAX_COUNT_RATE_HI',
			'MAX_COUNT_RATE_LO',
			'CR_FAIL_BRIGHT',
			'HV_MAX_CYCLES',
			'HV_LOW_SAFETY',
			'DAC_ADC_FACTOR',
			'HV_MCP_TOL',
			'HV_FAIL_MCP_V',
			'HV_MAX_STRIP_I',
			'HV_FAIL_STRIP_I',
			'HV_MIN_ANODE_V',
			'HV_MAX_ANODE_V',
			'HV_FAIL_ANODE_V',
			'MAX_OAP_MIR_1_TEMP',
			'MAX_OAP_MIR_2_TEMP',
			'MAX_GRAT_1_TEMP',
			'MAX_GRAT_2_TEMP',
			'MAX_SOC_MIR_TEMP',
			'MAX_CNDH_TEMP',
			'MAX_HVPS_TEMP',
			'MAX_LVPS_TEMP',
			'MAX_SOL_PORT',
			'MAX_DET_B_TEMP',
			'MAX_DET_E_TEMP',
			'MAX_CHASSIS_TEMP',
			'MAX_RADFET_TEMP',
			'MAX_TEMP_FAIL_CNT',
			'MAX_3P3_CUR_IDLE',
			'MAX_3P3_CUR_OPS',
			'MAX_3P3_FAIL_CNT',
			'MAX_P6P1_CUR_IDLE',
			'MAX_P6P1_CUR_OPS',
			'MAX_P6P1_FAIL_CNT',
			'MAX_M6P1_CUR_IDLE',
			'MAX_M6P1_CUR_OPS',
			'MAX_M6P1_FAIL_CNT',
			'SAFETY_MASK',
			'SAFETY_TIMEOUT_HI',
			'SAFETY_TIMEOUT_LO',
			'DEBUG_REPORT',
			'DEBUG_TEST',
			'SPARE_BYTE_171',
			'SPARE_BYTE_172',
			'SPARE_BYTE_173',
			'SPARE_BYTE_174',
			'SPARE_BYTE_175',
			'SPARE_BYTE_176',
			'SPARE_BYTE_177',
			'SPARE_BYTE_178',
			'SPARE_BYTE_179',
			'SPARE_BYTE_180',
			'SPARE_BYTE_181',
			'WRITE_CYCLES_HI',
			'WRITE_CYCLES_LO',
			],
	'uvs_param_storage_load':[
			'NOMINAL',
			'STORE_1',
			'STORE_2',
			'STORE_3',
			'HARDCODED_DEFAULT',
			],
	'uvs_select_toggle':[
			'DESELECT',
			'SELECT',
			],
	'uvs_test_pattern':[
			'ACTUAL',
			'EVENT_TABLE_BASED',
			],
}

cmdDict = {
	'UVS_NO_OP':{
		'opcode':'0xFD0E',
		'args': []
		},
	'UVS_RESET_COUNTER':{
		'opcode':'0xFD43',
		'args': [
			{'name':'counter_id','type':'uvs_counter_id','length':8,'range_min':None,'range_max':None},
			{'name':'overflow_counter','type':'uvs_overflow_counter','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_POWER_ON':{
		'opcode':'0xFD4D',
		'args': []
		},
	'UVS_RESET_INSTRUMENT':{
		'opcode':'0xFD4E',
		'args': []
		},
	'UVS_ABORT':{
		'opcode':'0xFD4F',
		'args': []
		},
	'UVS_CMD_DOOR':{
		'opcode':'0xFD53',
		'args': [
			{'name':'uvs_ap_door_state','type':'uvs_door_state','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_hp_door_state','type':'uvs_door_state','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_CRITICAL_CONFIRM':{
		'opcode':'0xFD54',
		'args': [
			{'name':'uvs_op_code','type':'uvs_critical_confirm','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_CONTROL_DECON_HTR':{
		'opcode':'0xFD55',
		'args': [
			{'name':'uvs_oap_heater','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_pickoff_heater','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_grating_heater','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_decon_htr_setpoint','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_SET_PARAM':{
		'opcode':'0xFD56',
		'args': [
			{'name':'uvs_parameter_index','type':'uvs_param_index','length':16,'range_min':None,'range_max':None},
			{'name':'uvs_parameter_value','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_START_HIST_ACQ':{
		'opcode':'0xFD57',
		'args': [
			{'name':'uvs_aid','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'uvs_apdoor','type':'uvs_close_open','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_hpdoor','type':'uvs_close_open','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_mask_enable','type':'uvs_enable_disable','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_lut_selection','type':'uvs_lut_select','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_pattern','type':'uvs_test_pattern','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_bin_id','type':'unsigned_arg','length':8,'range_min':0,'range_max':7},
			{'name':'uvs_pulse_height_en','type':'uvs_enable_disable','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_count_depth','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_acquisition_duration','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},
			{'name':'uvs_exposure_duration','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_START_PIX_ACQ':{
		'opcode':'0xFD58',
		'args': [
			{'name':'uvs_aid','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'uvs_apdoor','type':'uvs_close_open','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_hpdoor','type':'uvs_close_open','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_masking_active','type':'uvs_enable_disable','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_lut_selection','type':'uvs_lut_select','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_pattern','type':'uvs_test_pattern','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_bin_id','type':'unsigned_arg','length':8,'range_min':0,'range_max':7},
			{'name':'uvs_acquisition_dur','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_STORE_PARAMS_NV':{
		'opcode':'0xFD5A',
		'args': []
		},
	'UVS_LOAD_PARAM_NV':{
		'opcode':'0xFD5B',
		'args': [
			{'name':'uvs_param_storage_load','type':'uvs_param_storage_load','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_RESET_DATA_IF':{
		'opcode':'0xFD5C',
		'args': []
		},
	'UVS_CLOSE_AP':{
		'opcode':'0xFD5D',
		'args': []
		},
	'UVS_COUNTRATE_REPORTING':{
		'opcode':'0xFD5F',
		'args': [
			{'name':'uvs_analog_countrate','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_digital_countrate','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_discriminated_countrate','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_masked_countrate','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_band_rate_1','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_band_rate_2','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_band_rate_3','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_band_rate_4','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_band_rate_5','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_sampling_rate','type':'unsigned_arg','length':8,'range_min':0,'range_max':255},

		      ]
		},
	'UVS_STIM_CONTROL':{
		'opcode':'0xFD60',
		'args': [
			{'name':'uvs_stim_generation','type':'uvs_enable_disable','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_SET_DET_DISCRIM':{
		'opcode':'0xFD61',
		'args': [
			{'name':'uvs_det_lower_limit','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_det_upper_limit','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_START_HV_RAMP':{
		'opcode':'0xFD62',
		'args': [
			{'name':'uvs_hv_ramp_rate','type':'unsigned_arg','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_DEACTIVATE_HV':{
		'opcode':'0xFD63',
		'args': []
		},
	'UVS_ACTIVATE_ACTUATOR':{
		'opcode':'0xFD64',
		'args': [
			{'name':'uvs_actuator_select','type':'uvs_actuator_select','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_SET_LUT':{
		'opcode':'0xFD65',
		'args': [
			{'name':'uvs_lut','type':'uvs_lut','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_lut_pos_1','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_1','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_2','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_2','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_3','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_3','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_4','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_4','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_5','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_5','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_6','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_6','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_7','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_7','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_pos_8','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},
			{'name':'uvs_lut_val_8','type':'unsigned_arg','length':16,'range_min':0,'range_max':4095},

		      ]
		},
	'UVS_STORE_LUT_NV':{
		'opcode':'0xFD66',
		'args': [
			{'name':'uvs_lut_set','type':'uvs_lut_set','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_LOAD_LUT':{
		'opcode':'0xFD67',
		'args': [
			{'name':'uvs_lut_load','type':'uvs_lut_load','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_MEMORY_DUMP':{
		'opcode':'0xFD68',
		'args': [
			{'name':'uvs_mem_bank_dump','type':'uvs_memory_bank','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_address_dump','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'uvs_size_mem_dump','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_MEMORY_CHECK':{
		'opcode':'0xFD69',
		'args': [
			{'name':'uvs_mem_check_bank','type':'uvs_memory_bank','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_address','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},
			{'name':'uvs_size_check','type':'unsigned_arg','length':32,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_SELF_TEST':{
		'opcode':'0xFD6A',
		'args': [
			{'name':'uvs_test_unused_ram','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_nvram_1_4','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_current_execute_checksum','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_param_file_redundancy','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_lut_1_2','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_lut_3_4','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_lut_5_6','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_lut_7_8','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_lut_9_10','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_acq_mem_side_a','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_acq_mem_side_b','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_test_acq_mem_bank_switch','type':'uvs_select_toggle','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_START_PROGRAM':{
		'opcode':'0xFD6B',
		'args': [
			{'name':'uvs_page','type':'uvs_page','length':8,'range_min':None,'range_max':None},
			{'name':'uvs_start_address','type':'unsigned_arg','length':16,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_TEST_PANIC':{
		'opcode':'0xFD6C',
		'args': []
		},
	'UVS_SEND_CMD_FILE':{
		'opcode':'0xFD82',
		'args': [
			{'name':'command_file_path','type':'var_string_arg','length':1024,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_POWER_OFF':{
		'opcode':'0xFEAA',
		'args': []
		},
	'UVS_POWER_OFF_IMM':{
		'opcode':'0xFEAB',
		'args': []
		},
	'UVS_SET_MODE':{
		'opcode':'0xFF1F',
		'args': [
			{'name':'uvs_mode','type':'uvs_mode','length':8,'range_min':None,'range_max':None},

		      ]
		},
	'UVS_DMP_HS_PACKETS':{
		'opcode':'0xFF68',
		'args': [
			{'name':'dp_priority','type':'unsigned_arg','length':8,'range_min':0,'range_max':100},
			{'name':'hs_pkt_collection_duration','type':'unsigned_arg','length':32,'range_min':0,'range_max':86400},

		      ]
		},
	'SFP_UVS_RECOVERY_COUNT_CLR':{
		'opcode':'0xFF9E',
		'args': []
		},
}
