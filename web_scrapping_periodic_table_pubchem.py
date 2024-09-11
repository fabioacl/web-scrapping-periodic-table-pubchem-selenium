from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import numpy as np
import os

if __name__ == "__main__":
    # Safari WebDriver can be changed to Chrome or Firefox.
    driver = webdriver.Safari()

    # Target URL
    URL = "https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list"
    driver.get(URL)

    # CSV file path in the current working directory
    current_directory = os.getcwd()
    save_filepath = os.path.join(current_directory, "scraped_data.csv")

    if driver is not None:
        driver.get(URL)
        
        # Wait until the elements are visible
        try:
            # Wait until the periodic table list is available
            atoms_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="list-none space-y-8"]'))
            )
            
            atoms = driver.find_elements(By.XPATH, '//ul[@class="list-none space-y-8"]')
            
            if len(atoms) == 0:
                print("No elements found.")
                driver.quit()
                exit()

            atoms_info_split = atoms[0].text.split("\n")
            atoms_data = []
            atom_data = []
            new_atom = False
            CHARACTERISTICS_LIST = ["Atomic Mass", 
                                    "Electron Configuration", 
                                    "Oxidation States", 
                                    "Electronegativity (Pauling Scale)",
                                    "Atomic Radius (van der Waals)",
                                    "Ionization Energy",
                                    "Electron Affinity",
                                    "Melting Point",
                                    "Boiling Point",
                                    "Density",
                                    "Year Discovered"]

            for idx, row in enumerate(atoms_info_split):
                # After the atomic number there comes the atom data
                if row.isdigit():
                    new_atom = True
                    if idx > 0:
                        atoms_data.append(atom_data)  
                    atom_data = []
                else:
                    new_atom = False

                # Get which atom characteristic is being read
                atom_characteristic = next((i for i in CHARACTERISTICS_LIST if i in row), "")
                
                # Electron configuration and oxidation states are special cases
                if "Electron Configuration" in atom_characteristic or "Oxidation States" in atom_characteristic:
                    end_index = row.find(atom_characteristic) + len(atom_characteristic) + 1
                    atom_data.append([atom_characteristic, row[end_index:]])
                else:
                    found_numbers = re.findall(r'[+-]?\d+\.?\d*', row)
                    if len(found_numbers) > 0:
                        if atom_characteristic == "":  # The row with the atomic number does not have a string identifying it.
                            atom_data.append(["Atomic Number", float(found_numbers[0])])
                        else:
                            atom_data.append([atom_characteristic, float(found_numbers[0])])

            atoms_data_to_dataframe = []
            columns_dataframe = ["Atomic Number"] + CHARACTERISTICS_LIST

            for atom_data in atoms_data:
                atom_data_to_dataframe = []
                # Distribute the values within the rows through the possible columns
                for column in columns_dataframe:
                    column_found = False
                    for row in atom_data:
                        if column in row:
                            atom_data_to_dataframe.append(row[1])
                            column_found = True
                            break
                    # If a certain column is not in the atom data, then populate it with NaN
                    if not column_found:
                        atom_data_to_dataframe.append(np.nan)

                atoms_data_to_dataframe.append(atom_data_to_dataframe)

            # Convert the data to pandas DataFrame
            atoms_dataframe = pd.DataFrame(atoms_data_to_dataframe, columns=columns_dataframe)
            atoms_dataframe.to_csv(save_filepath, index=False)
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            driver.quit()
    else:
        print("Web browser not found.")
