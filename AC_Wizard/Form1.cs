namespace AC_Wizard
{
	using System;
	using System.Diagnostics;
	using System.IO;
	using System.Text;

	using Programs;
	using Wz_Prog = Programs.Wizard_Program;
	//using Prog_Mng = Programs.Program_Manager;

	public partial class Form1 : Form
	{
		Project_Managing Proj_Mng = new();
		Program_Manager Prog_Mng = new();

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
			Refresh_Tree(Proj_Mng.Get_Project_Root_Folder(), 0);
		}
		
		private string Refresh_Tree(string curr_dir, int level, TreeNode? parent_node = null)
		{
			//This function shall only be called without 'parent_node' when it is to refresh from the root.

			// Get files list:
			string[] item_list = Proj_Mng.Get_Items_inPath(curr_dir, true, 0);
			string[] item_path_list = Proj_Mng.Get_Items_inPath(curr_dir, false, 0);
			// Get folders list:
			string[] folder_list = Proj_Mng.Get_Items_inPath(curr_dir, true, 1);
			string[] folder_path_list = Proj_Mng.Get_Items_inPath(curr_dir, false, 1);
			bool can_next_level = false;

			treeView1.BeginUpdate();

			
			
			

			

			if (parent_node == null) //If this function is being called from 'root'...
				treeView1.Nodes.Clear(); //Clear all nodes.
			else
				parent_node.Nodes.Clear(); // If not, just clear all nodes inside the selected node


			string list_data = "";

			for (int i = 0; i < item_list.Length; i++) // Iterate items in root folder
			{
				if (Path.GetExtension(item_list[i]) != ".list")
					list_data += item_list[i] + "\n";
					
				//See if current file has a correspondent folder.
				/*
				*/

				
				if (parent_node == null)
					treeView1.Nodes.Add(item_list[i]);
				else
					parent_node.Nodes.Add(item_list[i]);
				
			}

			for (int j = 0; j < folder_list.Length; j++) // Iterate folders in root folder
			{
				
				TreeNode new_node;
				if (parent_node == null)
					new_node = treeView1.Nodes.Add(folder_list[j]);
				else
					new_node = parent_node.Nodes.Add(folder_list[j]); //

				can_next_level = true;




				//list_data += new_node.Text;
				//list_data += "\t" + Refresh_Tree(folder_path_list[j], level + 1, parent_node: new_node);
				String received = Refresh_Tree(folder_path_list[j], level + 1, parent_node: new_node);
				String[] aux_list = received.Split("\n");
				for (int l = 0; l < aux_list.Length; l++)
				{
					list_data += "\t" + aux_list[l] + "\n";


				}


				
				
			}
			treeView1.EndUpdate();
			return list_data;
		}

		private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
			
		}

		private void treeView1_NodeMouseDoubleClick(object sender, TreeNodeMouseClickEventArgs e)
		{
			//label1.Text = treeView1.SelectedNode.FullPath;
			if (openProgramDialog.ShowDialog() == DialogResult.OK)
			{
				
				string program_path = openProgramDialog.FileName;
				Proj_Mng.Open_File_inProject(treeView1.SelectedNode.FullPath, program_path);
			}
		}

		private void openProgramDialog_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
		{
			
		}


		
		private void btnProgramStuff_Click(object sender, EventArgs e)
        {
			
			if (openProgramDialog.ShowDialog() == DialogResult.OK)
			{
				string program_path = openProgramDialog.FileName;
				Prog_Mng.btnPush(program_path);
			}
			

			
		}

        private void label2_Click(object sender, EventArgs e)
        {
			label2.Text = Refresh_Tree(Proj_Mng.Get_Project_Root_Folder(), 0);
		}
    }
}