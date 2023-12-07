import random
import string


"""
*Utility script to generate positive test data for the execution
*Take the schemas for the input field from the user in master_databuilder excel sheet
*To run the script in Gitbash use command 'python -u utils/ui_libs.py'
"""
class OF_TYPE():
    def OF_TYPE(self, **kwargs):
        # checking # OF_TYPE( max = 10, min = 2, method = 'min', value = 'Number' )
        positiveValues = []
        if 'Boolean' in kwargs.values():
            positiveValues.append('True')
            positiveValues.append('False')
        else:
            kwargs_values = list(kwargs.values())
            min = int(kwargs['min'])
            max = int(kwargs['max'])
            method = kwargs['method']

            alpha_kwargs = "Static:Alpha-" + str(max)
            alpha_kwargs = alpha_kwargs[:-1] + kwargs_values[0][-1]
            alphanumeric_kwargs = "Static:Alphanumeric-" + str (max)
            alphanumeric_kwargs = alphanumeric_kwargs[:-1] + kwargs_values[0][-1]
            numeric_kwargs = "Static: Numeric-" + str (max)
            numeric_kwargs = numeric_kwargs[:-1] + kwargs_values[0][-1]

            if "Alphanumenic" in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase + string.digits
            elif "alphanumeric_kwargs" in kwargs.values(()):
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase + string.digits
            elif "numeric_kwargs" in kwargs.values():
                ranStrSameType = string.digits
            elif "Numeric" in kwargs.values():
                ranStrSameType = string.digits
            elif 'Alpha' in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase
            elif "alpha_kwargs" in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase
            elif 'Hexadecimal' in kwargs.values():
                 ranStrSameType = '0123456789abcdef'

        if method == 'class':
            k = random.randint(min, max)
            posValueInRange = "".join(random.choices(ranStrSameType, k=k))
            # generate negative value in range, sai
            positiveValues.insert (0, posValueInRange)

        elif method == "min":
            posValueInMinRange = "".join(random.choices(ranStrSameType, k=min))
            positiveValues.insert (0, posValueInMinRange)

        elif method =='max':
            posValueInMaxRange = "".join(random. choices(ranStrSameType, k=max))
            positiveValues.insert(0, posValueInMaxRange)

        return positiveValues[0]


class NOT_OF_TYPE():
    def NOT_OF_TYPE(self, **kwargs):
        # checking # OF_TYPE( max = 10, min = 2, method = 'min', value = 'Number' )
        negativeValues = []
        if 'Boolean' in kwargs.values():
            negativeValues.append('True')
            negativeValues.append('False')
        else:
            kwargs_values = list(kwargs.values())
            min = int(kwargs['min'])
            max = int(kwargs['max'])
            method = kwargs['method']

            if "Alphanumenic" in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase + string.digits
                ranStrOtherType = string.punctuation
            elif "Numeric" in kwargs.values():
                ranStrSameType = string.digits
                ranStrOtherType = string.ascii_uppercase + string.ascii_lowercase + string.punctuation
            elif 'Alpha' in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase
                ranStrOtherType = string.digits +  string.punctuation
            elif 'Hexadecimal' in kwargs.values():
                ranStrSameType = '0123456789abcdef'
                ranStrOtherType = string.punctuation
            elif "Static" in kwargs.values():
                ranStrSameType = string.ascii_uppercase + string.ascii_lowercase + string.digits
                ranStrOtherType = string.ascii_uppercase + string.ascii_lowercase + string.punctuation + string.digits

        if method == 'class':
            k = random.randint(min, max)

            negValueInRange = "".join(random.choices(ranStrOtherType, k=k))
            # generate negative value in range, sai
            negativeValues.insert(0, negValueInRange)

        elif method == "min":
            negValueInRange = "".join(random.choices(ranStrOtherType, k=min-1))
            negativeValues.insert (0, negValueInRange)

        elif method =='max':
            negValueInRange = "".join(random. choices(ranStrOtherType, k=max+1))
            negativeValues.insert(0, negValueInRange)

        return negativeValues[0]

class MANDATORY():
    def MANDATORY(self, **kwargs):

        method = kwargs['method']

        if method == "EMPTY":
            return ""