How to create a new pilot
=========================================
Hint: To see it on a live example:
:doc:`Create a Qunicorn-Pilot <pilot_tutorial_demo>`


1. Create a new python file in the `qunicorn_core.core.pilotmanager` directory. The naming pattern is: [provider]_pilot.py

2. For the creation you can also just copy the base_pilot.py file and rename it.

3. After at least creating the Pilot class inside extending from the base_pilot add your pilot to the "PILOTS" list in the pilotmanager.py file.

4. Add your pilot to the `qunicorn_core.core.pilotmanager` directory in the `__init__.py` file.

5. Implement your pilot


Implement your pilot
--------------------

1. Define the provider_name by adding a new enum value to the ProviderName.py enum. And set it as your provider_name.

2. Define the supported_languages. If necessary add a new enum value to the AssemblerLanguage.py enum or use an already existing one.

3. Implement all methods that raise a "NotImplementedError" in the base_pilot.py file.

4. Check out the comments in the base_pilot.py file for more information about the methods and also find some examples in the aws_pilot or ibm_pilot file.


Change the transpile and preprocessing manager if necessary
-----------------------------------------------------------

1. This is only necessary if you added a new assembler language to the AssemblerLanguage.py file.

2. If your circuit in the language is a string but should be handled as an object, you need to add an annotated method to the preprocessing manager.
   This method should then return a circuit object instead of a string.
   One example method would be preprocess_braket.

3. The next step is to also add some annotated methods to the transpile_manager.
   Here you find some examples at the bottom of the file.
   You should add a method to transpile your language to one already existing.
   And also add a method to transpile from one already existing to your language.


Add some tests and documentation
--------------------------------

1. Add some tests to the `qunicorn_core.core.tests` directory. Use the principles written in the tests/README.md file.

2. If there exists a local executor (simulator?) you can add your tests to the automated_tests directory.
   Otherwise use the manual_tests directory.

3. If you added a new assembler language and pilot you can use the method `test_utils.execute_job_test` like it is done in the `test_ibm_job_execution.py` file.

4. Write comments and documentation to your new implemented code, if there are some special architectural decisions you should also add them to the documentation.

5. Checkout the tests from the `test_pilots_default_data.py` file to avoid creating the same tests twice.
