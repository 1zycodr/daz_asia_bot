class CallbackTypes:
    NOMINATION = 'nom'
    MODEL = 'mod'
    INVALID_CALLBACK = 'inv'
    UNKNOWN = 'unk'
    NEXT_PHOTO = 'nxt'
    PREV_PHOTO = 'prv'
    VOTE = 'vot'
    START = 'strt'
    ALREADY_VOTED = 'avtd'
    ABOUT = 'abut'
    
    @staticmethod
    def set_nomination(nomination_id):
        return CallbackTypes.NOMINATION + str(nomination_id)
    
    
    @staticmethod
    def set_model(model_id, nomination_id):
        return CallbackTypes.MODEL + str(model_id) + \
            '|' + str(nomination_id)

    
    @staticmethod
    def set_next_photo(model_id, photo_ind, nomination_id):
        return CallbackTypes.NEXT_PHOTO + \
            str(model_id) + '|' + str(photo_ind) + \
            '|' + str(nomination_id)


    @staticmethod
    def set_prev_photo(model_id, photo_ind, nomination_id):
        return CallbackTypes.PREV_PHOTO + \
            str(model_id) + '|' + str(photo_ind) + \
            '|' + str(nomination_id)


    @staticmethod
    def set_vote(model_id, photo_ind, nomination_id):
        return CallbackTypes.VOTE + \
            str(model_id) + '|' + str(photo_ind) + \
            '|' + str(nomination_id)


    @staticmethod
    def set_already_voted():
        return CallbackTypes.ALREADY_VOTED


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
                try:
                    model_id, nomination_id = callback_data[3:].split('|')
                except ValueError:
                    return '', '', 'callback type is model, but invalid model_id or nomination_id'

                if model_id.isdigit() and nomination_id.isdigit():
                    return CallbackTypes.MODEL, (int(model_id), int(nomination_id)), None
                else:
                    return '', '', 'callback type is model, but invalid type of model_id of nomination_idd'

            elif callback_data[:4] == CallbackTypes.START:
                return CallbackTypes.START, '', None

            elif callback_data[:3] == CallbackTypes.NEXT_PHOTO:
                try:
                    model_id, photo_ind, nomination_id = callback_data[3:].split('|')
                except ValueError:
                    return '', '', 'callback type is next photo, but invalid model_id or photo_ind or nomination_id'
                
                if model_id.isdigit() and photo_ind.isdigit() and nomination_id.isdigit():
                    return CallbackTypes.NEXT_PHOTO, (int(model_id), int(photo_ind), int(nomination_id)), None
                else:
                    return '', '', 'callback type is next photo, but invalid type of model_id or photo_ind or nomination_id'

            elif callback_data[:3] == CallbackTypes.PREV_PHOTO:
                try:
                    model_id, photo_ind, nomination_id = callback_data[3:].split('|')
                except ValueError:
                    return '', '', 'callback type is prev photo, but invalid model_id or photo_ind or nomination_id'
                
                if model_id.isdigit() and photo_ind.isdigit() and nomination_id.isdigit():
                    return CallbackTypes.PREV_PHOTO, (int(model_id), int(photo_ind), int(nomination_id)), None
                else:
                    return '', '', 'callback type is prev photo, but invalid type of model_id or photo_ind or nomination_id'
            
            elif callback_data[:4] == CallbackTypes.ALREADY_VOTED:
                return CallbackTypes.ALREADY_VOTED, None, None

            elif callback_data[:3] == CallbackTypes.VOTE:
                try:
                    model_id, photo_ind, nomination_id = callback_data[3:].split('|')
                except ValueError:
                    return '', '', 'callback type is vote, but invalid model_id or photo_ind or nomination_id'
                
                if model_id.isdigit() and photo_ind.isdigit() and nomination_id.isdigit():
                    return CallbackTypes.VOTE, (int(model_id), int(photo_ind), int(nomination_id)), None
                else:
                    return '', '', 'callback type is vote, but invalid type of model_id or photo_ind or nomination_id'

            elif callback_data[:4] == CallbackTypes.ABOUT:
                return CallbackTypes.ABOUT, None, None                

            else:
                return CallbackTypes.UNKNOWN, '', None
        else:
            return '', '', 'callback data is less than 4 in length'