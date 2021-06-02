class CallbackTypes:
    NOMINATION = 'nom'
    MODEL = 'mod'
    INVALID_CALLBACK = 'inv'
    UNKNOWN = 'unk'

    @staticmethod
    def set_nomination(nomination_id):
        return CallbackTypes.NOMINATION + str(nomination_id)
    
    
    @staticmethod
    def set_model(model_id):
        return CallbackTypes.MODEL + str(model_id)

    
    @staticmethod
    def get_type(callback_data):

        if not isinstance(callback_data, str):
            return '', '', 'callback data is not str!'

        if len(callback_data) >= 4: 
            if callback_data[:3] == CallbackTypes.NOMINATION:
                nomination_id = callback_data[3:]

                if nomination_id.isdigit():
                    return CallbackTypes.NOMINATION, int(nomination_id), None
                else: 
                    return '', '', 'callback type is nomination, but with invalid id'

            elif callback_data[:3] == CallbackTypes.MODEL:
                model_id = callback_data[3:]

                if model_id.isdigit():
                    return CallbackTypes.MODEL, int(model_id), None
                else:
                    return '', '', 'callback type is model, but with invalid id'
                    
        else:
            return '', '', 'callback data is less than 4 in length'