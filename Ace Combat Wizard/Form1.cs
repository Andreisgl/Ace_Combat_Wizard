using System.Text;
using PAC_Utility;
namespace Ace_Combat_Wizard
{
    public partial class Form1 : Form
    {
        Stream_Manager Stream_Mng = new Stream_Manager();
        PAC_Handler PAC_Hndlr = new PAC_Handler();
        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (openFileDialog1.ShowDialog() == DialogResult.OK)
            {
                string file_path = openFileDialog1.FileName;
                label1.Text = file_path;

                byte[] raw_bytes = Stream_Mng.Stream_Extractor(file_path);


                string hex = BitConverter.ToString
                (
                PAC_Hndlr.TBL_reader(raw_bytes)
                );
                
                label2.Text = hex;
            }
        }
    }
}