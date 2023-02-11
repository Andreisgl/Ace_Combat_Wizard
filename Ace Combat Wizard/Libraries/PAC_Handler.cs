using System;

namespace PAC_Utility
{
	public class PAC_Handler
	{
		public PAC_Handler()
		{
		}

		public byte[] TBL_reader(byte[] input_stream)
		{
			int index = 0;
			int stream_length = input_stream.Length;
			//Read number of files

			byte[] n_files = new byte[4];
			for (int i = 0; i < 4; i++)
			{
				n_files[i] = input_stream[index + i];
				index++;
            }


			return n_files;
			//byte[] return_placeholder = {(byte)0, (byte)0 };
			//return return_placeholder;
        }
	}
}