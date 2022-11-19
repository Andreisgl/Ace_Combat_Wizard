using System;
using System.Text;
using System.Diagnostics;

namespace AC_Wizard
{
	public class Project_Managing
	{
		readonly string cwd = Directory.GetCurrentDirectory();

		string PROJECT_FOLDER = "Projects";
		readonly string project_info_filename = "project_info";
		readonly string project_info_file_extension = ".ACWProj";

		string project_info_file = "";

		string PROJECT_ROOT_FOLDER_NAME = "proot";
		string PROJECT_ROOT_FOLDER = "";

		string curr_project_path = "";

		public Project_Managing()
		{
			project_info_filename += project_info_file_extension;
		}
		public bool Is_Project(string path)
		{
			project_info_file = Path.Join(path, project_info_filename);
			if (File.Exists(project_info_file))
			{
				//Console.WriteLine("Project file exists!");
				return true;
			}
			else
			{
				//Console.WriteLine("Project file does not exist!");
				return false;
			}
		}

		public void Check_folders()
		{
			PROJECT_FOLDER = Path.Join(cwd, PROJECT_FOLDER);


			if (!Directory.Exists(PROJECT_FOLDER))
			{
				Directory.CreateDirectory(PROJECT_FOLDER);
			}
		}
		public void Check_Project_Folders(string project_path)
        {
			PROJECT_ROOT_FOLDER = Path.Join(project_path, PROJECT_ROOT_FOLDER_NAME);
			if (!Directory.Exists(PROJECT_ROOT_FOLDER))
			{
				Directory.CreateDirectory(PROJECT_ROOT_FOLDER);
			}
		}
		public string Get_Project_Folder()
        {
			return PROJECT_FOLDER;
		}
		public string Get_Project_Root_Folder()
		{
			return PROJECT_ROOT_FOLDER;
		}

		public bool Open_Project(string project_path)
        {
			// Check if chosen path is a valid project...
			if (Is_Project(project_path))
			{
				//If so, open it.
				curr_project_path = project_path;
				Check_Project_Folders(project_path);
			}
			else // If not:
			{
				if (Create_Project(project_path))
					return true;
				return false;
			}
			return true;
		}

		public bool Create_Project(string path)
		{
			//Directory.CreateDirectory(Path.Join(path, project_name));
			//File.Create(Path.Combine(path, project_name, project_info_filename)).Close();
			File.Create(Path.Combine(path, project_info_filename)).Close();
			return true;
		}
		public void Import_File_toRoot(string[] file_path)
		{
			string file_name = "";
			
			//Copies chosen file to root folder.
			for (int i = 0; i < file_path.Length; i++)
            {
				try
				{
					file_name = Path.GetFileName(file_path[i]);
					File.Copy(file_path[0], Path.Join(PROJECT_ROOT_FOLDER, file_name), false);
				}
				catch (IOException)
				{
					Debug.WriteLine(file_name + " already Exists!");
				}
			}
		}
		
		public string[] Get_Items_inDir(string directory)
		{
			//Some weird exception happens here...
			try
			{
				return System.IO.Directory.GetFiles(directory);
			}
			catch (System.ArgumentException)
			{
				string[] aux = {};
				return aux;
            }


		}
		public string[] Get_Folders_inDir(string directory)
		{
			return System.IO.Directory.GetDirectories(directory);
		}
		public string[] Get_Items_inPath(string path, bool only_file_name, int type_mode)
		{
			/*
			bool only_item_name:
				- true = return only item names
				- false = return whole path
			int type_mode:
				- 0 = return files only
				- 1 = return folders only */

			string[] root_list = Get_Items_inDir(path);

			switch (type_mode)
			{
				case 0: // Files only
					root_list = Get_Items_inDir(path);
					break;
				case 1: // Folders only
					root_list = Get_Folders_inDir(path);
					break;
				default:
					root_list = Get_Items_inDir(path);
					break;
			}
			if (only_file_name)
			{
				for(int i=0; i< root_list.Length; i++)
					root_list[i] = Path.GetFileName(root_list[i]);
			}
			return root_list;
		}
		public bool IsCorrespondent(string file, string folder)
		{	
			if (folder == GetCorrespondent(file, true))
				return true;
			else
				return false;
		}

		public string GetCorrespondent(string file, bool isFile)
		{
			// Returns the correspondent name for the input
			// if isFile == true, generate the name it's folder should have
			// if isFile == false, generate the name it's file should have
			char original_char;
			char new_char;

			if (isFile)
			{
				original_char = '.';
				new_char = '—';
			}
			else
			{
				original_char = '—';
				new_char = '.';
			}

			
			int replace_index = file.LastIndexOf(original_char);


			//file = file.Substring(0, replace_index) + new_char + file.Substring(replace_index + 1);
			char[] aux = file.ToCharArray();
			aux[replace_index] = new_char;
			file = new string(aux);
			

			//file = file.Replace(original_char, new_char);
			return file;
			
		}

		public void Open_File_inProject(string input_path, string program_path)
		{
			input_path = Path.Join(PROJECT_ROOT_FOLDER, input_path);
			string dest_path = "";

			//Choose destination File/Folder
			if (File.Exists(input_path))
			{
				// This path is a file
				dest_path = Path.Join( Path.GetDirectoryName(input_path),
				Path.GetFileNameWithoutExtension(GetCorrespondent(input_path, true)) );
				
			}
			else if (Directory.Exists(input_path))
			{
				// This path is a directory
				dest_path = Path.GetDirectoryName(input_path);
			}

			// WHY DO THIS?!
			//Simple: Creating a '.bat' and then running it saves me the trouble of integrating with Python!

			string args = $"\"{input_path}\" \"{dest_path}\"";

			// Run file
			string run_file_name = "./ACWRun.bat";
			string full_string = $"chcp 65001\nStart \"\" \"{program_path}\" {args}";

			File.WriteAllText(run_file_name, full_string);
			Process ExternalProcess = new Process();
			ExternalProcess.StartInfo.FileName = run_file_name;
			ExternalProcess.StartInfo.WindowStyle = ProcessWindowStyle.Maximized;
			ExternalProcess.Start();
			ExternalProcess.WaitForExit();
		}
	}
}