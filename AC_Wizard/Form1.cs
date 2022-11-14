namespace AC_Wizard
{
	using System;
	using System.Diagnostics;
	using System.IO;
	using System.Text;
	public partial class Form1 : Form
	{
		Project_Managing Proj_Mng = new();
		public Form1()
		{
			InitializeComponent();
		}

		private void Form1_Load(object sender, EventArgs e)
		{
			Proj_Mng.Check_folders();
			projectBrowserDialog1.InitialDirectory = Proj_Mng.Get_Project_Folder();

			btnOpenFile.Enabled = false;
			btnRefresh.Enabled = false;
		}

		private void btnOpenFile_Click(object sender, EventArgs e)
		{
			if (openFileDialog1.ShowDialog() == DialogResult.OK)
			{
				string[] file_name = new string[(openFileDialog1.FileNames.Length)];
				file_name = openFileDialog1.FileNames;
				Proj_Mng.Import_File_toRoot(file_name);
			}
			
		}

		private void openFileDialog1_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
		{      
			//Process.Start(openFileDialog1.FileName);
		}


		private string project_path = "";
		private void btnOpenProject_Click(object sender, EventArgs e)
		{
			if (projectBrowserDialog1.ShowDialog() == DialogResult.OK)
			{
				project_path = projectBrowserDialog1.SelectedPath;
				
				
				if(Proj_Mng.Open_Project(project_path))
				{
					btnOpenFile.Enabled = true;
					btnRefresh.Enabled = true;
				}
				else
				{
					btnOpenFile.Enabled = false;
					btnRefresh.Enabled = false;
				}
			}
		}

		private void btnRefresh_Click(object sender, EventArgs e)
		{
			treeView1.BeginUpdate();
			treeView1.Nodes.Clear();
			//TreeNode root = treeView1.Nodes.Add("root");
			//treeView1.ExpandAll();
			Recursive_Tree_Stuff(Proj_Mng.Get_Project_Root_Folder(), 0);
			treeView1.EndUpdate();
		}

			

		
		private void Recursive_Tree_Stuff(string curr_dir, int level, TreeNode? parent_node = null)
		{
			Debug.WriteLine("curr_dir = " + curr_dir);
			
			// Provisory hard-code because I'm lazy!
				//It caused more problems than it solved!

			// Get files list:
			string[] item_list = Proj_Mng.Get_Items_inPath(curr_dir, true, 0);
			string[] item_path_list = Proj_Mng.Get_Items_inPath(curr_dir, false, 0);
			// Get folders list:
			string[] folder_list = Proj_Mng.Get_Items_inPath(curr_dir, true, 1);
			string[] folder_path_list = Proj_Mng.Get_Items_inPath(curr_dir, false, 1);

			//Check if there is any folder corresponding to a file
			/*CORE CONCEPT: ||| CORRESPONDENCE |||
				In order to make the file tree, we need to delve deeper
				and extract the components of each file.
				The contents of such extractions are kept in a correspondent folder.

				The correspondent folder for a file has the exact same name, except that
				the "." of the file extension is swapped out for "—" ("Em Dash", ALT+0151).
				This swapping is necessary, since a folder and a file with the same name
				cannot coexist.

				This correspondence will be kept in a bi-dimensional array,
				must any more of those correspondences be made
			*/
			// I'm commenting this until I find it's right place in the code!
			// char[,] SWAPPING_DICTIONARY = { {'.', '—' } };

			//treeView1.BeginUpdate();
			bool can_next_level = true;
			//int level = 0; // Level of the folder since the root
			Debug.WriteLine("l = " + level);
			can_next_level = false;
			
			for (int i = 0; i < item_list.Length; i++) // Iterate items in root folder
			{
				Debug.WriteLine("i = " + i);

				/*
				if (parent_node == null)
				{
					parent_node = treeView1.Nodes.Add(item_list[i]);
					//parent_node = item_list[i];
					//TreeNode new_node = parent_node.Nodes.Add(item_list[i]);
				}
				*/

				//See if current file has a correspondent folder.
				for (int j = 0; j < folder_list.Length; j++) // Iterate folders in root folder
				{
					Debug.WriteLine("j = " + j);
					if (Proj_Mng.Is_Correspondent(item_list[i], folder_list[j]))
					{
						//If it does, add the folder as a tree node instead of it.
						
						Debug.WriteLine("Corresponds!");
						//Add new node stuff here
						TreeNode new_node;
						if(parent_node == null)
						{
							new_node = treeView1.Nodes.Add(item_list[i]);
						}
						else
						{
							new_node = parent_node.Nodes.Add(item_list[i]); //
						}
						can_next_level = true;
						Debug.WriteLine("recur = " + folder_path_list[j]);

						Recursive_Tree_Stuff(folder_path_list[j], level + 1, parent_node: new_node);
					}
					else
					{
						can_next_level = false;
					}
				}
				//If it doesn't, just put it as the node.
				if (!can_next_level)
				{ 
					if (parent_node == null)
					{
						treeView1.Nodes.Add(item_list[i]);

					}
					else
					{
						parent_node.Nodes.Add(item_list[i]);

					}
				//TreeNode aux = parent_node.Nodes.Add(item_list[i]);
				}
				Debug.WriteLine("Does not correspond...");
			}
			
			//treeView1.EndUpdate();
		}
		
	}
}