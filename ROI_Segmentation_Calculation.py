''' 批量计算ROI和对应data的体积密度等参数 '''
def ROI_Segmentation_Calculation(input_folder, output_path, pair_state, label_value):

    # 判断是否是多标签
    if label_value == 'all':

        # 判断输入路径是pair数据
        if pair_state == 0:

            # 如果每个子类文件夹中不存在data和label的文件夹则报错
            if os.path.exists(os.path.join(input_folder, 'data')) and os.path.exists(os.path.join(input_folder, 'label')):

                data_file_lists = os.listdir(os.path.join(input_folder, 'data'))
                mask_file_lists = os.listdir(os.path.join(input_folder, 'label'))
                
                ROI_Statistics_init_name = ['ID', 'label value', 'voxel Count', 'Volume(mm3)', 'Intensity min', 'Intensity max', 'Intensity mean', 'Intensity std', 'Intensity var', 'Intensity sum', 'Intensity 25%', 'Intensity 50%', 'Intensity 75%']
                ROI_Statistics_init_csv = pd.DataFrame(columns = ROI_Statistics_init_name)
                ROI_Statistics_init_csv.to_csv(os.path.join(output_path, 'ROI_Statistics.csv'), index=False)

                for i in tqdm(range(len(data_file_lists))):
                    data_ds = sitk.ReadImage(os.path.join(input_folder, 'data', data_file_lists[i]))
                    mask_ds = sitk.ReadImage(os.path.join(input_folder, 'label', mask_file_lists[i]))
                    dataArr = sitk.GetArrayFromImage(data_ds)
                    maskArr_ori = sitk.GetArrayFromImage(mask_ds)

                    # 判断有哪些ROI
                    stats = sitk.LabelShapeStatisticsImageFilter()
                    stats.Execute(mask_ds)
                    labels_value = list(stats.GetLabels())
                    labels_nums = stats.GetNumberOfLabels()

                    for j in range(len(labels_value)):
                        maskArr = copy.deepcopy(maskArr_ori)

                        # 分别计算每一个mask的值
                        maskArr[maskArr!=labels_value[j]] = 0
                        maskArr[maskArr!=0] = 1

                        # 体积
                        counts = np.sum(maskArr == 1)
                        spacing = mask_ds.GetSpacing()  #order: x, y, z
                        unitVol = np.prod(spacing)
                        roiVol = unitVol * counts
            

                        # 均值标准差等
                        data_masked = dataArr * maskArr
                        exsit = (maskArr != 0)
                        mx = np.ma.masked_array(data_masked, mask=exsit)

                        # intensity_mean = np.mean(mx)
                        # intensity_std = np.std(mx)
                        # intensity_var = np.var(mx)
                        # intensity_max = np.max(mx)
                        # intensity_min = np.min(mx)
                        # # intensity_median = np.median(mx)
                        # intensity_sum = np.sum(mx)    


                        mx = data_masked[data_masked!=0].flatten()
                        intensity_mean = np.mean(mx)
                        intensity_std = np.std(mx)
                        intensity_var = np.var(mx)
                        intensity_max = np.max(mx)
                        intensity_min = np.min(mx)
                        intensity_median = np.median(mx)
                        intensity_sum = np.sum(mx)  
                        intensity_25_50_75 = np.percentile(mx, [25, 50, 75])

                        pd.DataFrame(np.column_stack((data_file_lists[i].split('.')[0], labels_value[j], counts, roiVol, intensity_min, intensity_max, intensity_mean, intensity_std, intensity_var, intensity_sum, intensity_25_50_75[0], intensity_25_50_75[1], intensity_25_50_75[2]))).to_csv(os.path.join(output_path, 'ROI_Statistics.csv'), index=False, mode='a', header=False)


            else:
                return 'no paired folders'