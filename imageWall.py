# This code can generate thumbnail images from whole slide images and visualise a lot of images in an image-wall.

import os
from PIL import Image
import sys
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import glob
import argparse
import csv
import openslide as openslide
import datetime
import math
import pandas as pd



# read input from csv file:
def read_csv_file(path_to_csv, do_sorting_based_on):
    imgTgs = []
    alg = []
    dates = []
    jbIDs = []
    sorting_based_on_this_col = []
    i = 0
    with open(path_to_csv, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if i == 0:
                idx_sorting = row.index(do_sorting_based_on)
                i = 1
            else:
                imgTgs.append(row[1])
                alg.append(row[2])
                dates.append(row[3].split(' ')[0])
                jbIDs.append(row[4])
                sorting_based_on_this_col.append(row[idx_sorting])
    sorting_based_on_this_col = [x for x in sorting_based_on_this_col if x]
    return alg, dates, imgTgs, jbIDs, sorting_based_on_this_col
    
# find the list of existing algorithms
def read_existing_algorithms(alg, tasks):
    unique_algs = [x for i, x in enumerate(alg) if i == alg.index(x)]
    print('---------------------------------------------------------------------------------------------------------')
    print('Existing Algorithms in the csv file are: \n')
    print(unique_algs)
    print('---------------------------------------------------------------------------------------------------------')
    print('User defined Algorithms to be shown in the wall mass review are: \n')
    print(tasks)

# cretae the folder name format in markups path
def read_dates(dates):
    unique_dates = [x for i, x in enumerate(dates) if i == dates.index(x)]
    print('---------------------------------------------------------------------------------------------------------')
    print('Existing Dates in the csv file are: \n')
    print(unique_dates)
    out_fs = []
    for fs in unique_dates:
        dt_obj = datetime.datetime.strptime(fs,'%m/%d/%Y')
        dt_obj1 = datetime.datetime.strftime(dt_obj + datetime.timedelta(days=1), '%Y-%m-%d')
        dt_obj2 = datetime.datetime.strftime(dt_obj + datetime.timedelta(days=2), '%Y-%m-%d')
        dt_obj3 = datetime.datetime.strftime(dt_obj + datetime.timedelta(days=3), '%Y-%m-%d')
        rcrd_date = datetime.datetime.strftime(dt_obj, '%Y-%m-%d')
        # make a series of folder options to look for the resulted images from HALO
        out_fs.append(rcrd_date)
        out_fs.append(dt_obj1)
        out_fs.append(dt_obj2)
        out_fs.append(dt_obj3)
        
    unique_dates2 = [x for i, x in enumerate(out_fs) if i == out_fs.index(x)]
    print('---------------------------------------------------------------------------------------------------------')
    print('Dates for which folders will be searched for are:\n')
    print(unique_dates2)
    return unique_dates2

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

# cretae the image name format in markups folder
def read_image_names(imgTgs, unique_dates):
    unique_imgTgs = [x for i, x in enumerate(imgTgs) if i == imgTgs.index(x)]
    out_Dict = {} # this dictionary contains the list of images for each case that will be shown as mass review
    for tgs in unique_imgTgs:
        indx1 =  [i for i,x in enumerate(imgTgs) if x==tgs] # find the list of outcomesfor a case
        list_of_names = []
        for i in indx1:
            if alg[i] in tasks:
                for dt in unique_dates:
                    if os.path.exists(os.path.join(path_to_markups,dt, imgTgs[i].replace(slideFormat,'')+'_job_'+jbIDs[i]+'_classifier'+input_format)):
                        list_of_names.append(os.path.join(path_to_markups,dt, imgTgs[i].replace(slideFormat,'')+'_job_'+jbIDs[i]+'_classifier'+input_format))
                    elif os.path.exists(os.path.join(path_to_markups,dt, imgTgs[i].replace(slideFormat,'')+'_job_'+jbIDs[i]+'_analysis'+input_format)):
                        list_of_names.append(os.path.join(path_to_markups,dt, imgTgs[i].replace(slideFormat,'')+'_job_'+jbIDs[i]+'_analysis'+input_format))
        out_Dict[tgs.replace(slideFormat,'')] = list_of_names  # output of the csv analysis
    out_Dict_sorted = sorted(out_Dict.keys(), key=lambda x:x.lower())
    print('---------------------------------------------------------------------------------------------------------')
    print('How many image files to be shown in the mass review wall?')
    print(len(out_Dict_sorted))
    print('---------------------------------------------------------------------------------------------------------')
    return out_Dict_sorted, out_Dict

# make a dictionary based on the user defined column to be sorted    
def mkDict_imgTgs_sortingCol(imgTgs, sorting_based_on_this_col):
    unique_imgTgs = [x for i, x in enumerate(imgTgs) if i == imgTgs.index(x)]
    out_Dict = {} # this dictionary contains the list of images for each case that will be shown as mass review
    for i,tgs in enumerate(unique_imgTgs):
        out_Dict[tgs] = float(sorting_based_on_this_col[i])
    return out_Dict
    
# do plotting on the wall
def do_plotting(value, ratio, total_summary_row, total_summary_col,iter, tsk0, case, tasks, only_raw):
    for v in value:
        if str2bool(only_raw) is True:
            if 'analysis' in v:
                slide = openslide.OpenSlide(filename=v)
                dim_slide = slide.level_dimensions[0]
                img = slide.get_thumbnail((dim_slide[0]/ratio, dim_slide[1]/ratio))
                ax = fig.add_subplot(total_summary_row, total_summary_col,iter)
                ax.imshow(img, aspect="auto")
                ax.set_title(r"$\bf{" + str(case) + "}$" + ' - ' + key, fontsize=34)
                case = case + 1
                tsk0 = 0
                ax.set_axis_off()
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                ax.set_aspect('equal')
                plt.subplots_adjust(wspace=0.1, hspace=0.05)
                iter = iter+1

        else:
            slide = openslide.OpenSlide(filename=v)
            dim_slide = slide.level_dimensions[0]
            img = slide.get_thumbnail((dim_slide[0]/ratio, dim_slide[1]/ratio))
            ax = fig.add_subplot(total_summary_row, total_summary_col,iter)
            ax.imshow(img, aspect="auto")
            
            if tsk0 == 0:
                ax.set_title(r"$\bf{" + str(case) + "}$" + ' - ' + key, fontsize=34)
                case = case + 1
                tsk0 = tsk0 + 1
            elif tsk0>0 and tsk0<len(tasks.split(','))-1:
                tsk0 = tsk0 + 1
            elif tsk0 == len(tasks.split(','))-1:
                tsk0 = 0

        ax.set_axis_off()
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.subplots_adjust(wspace=0.1, hspace=0.05)
        iter = iter+1
    return case, tsk0, iter
        
if __name__=='__main__':

    now1 = datetime.datetime.now()
    print("now =", now1)
    print('**************************')
    #==============================================================================================================================
    #                                         PART 0: read input file from the user
    #==============================================================================================================================
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()
    inputs = []
    for f in args.file:
        x = f.strip().split(':')[1].split('#')[0].strip()
        inputs.append(x)
    # --------------------------------------------
    cc = 0
    path_to_csv = inputs[cc]; cc = cc+1
    path_to_markups = inputs[cc]; cc = cc+1
    output_dir = inputs[cc]; cc = cc+1
    input_format = inputs[cc]; cc = cc+1
    output_format = inputs[cc]; cc = cc+1
    slideFormat = inputs[cc]; cc = cc+1
    study_name = inputs[cc]; cc = cc+1
    total_summary_col= int(inputs[cc]); cc = cc+1
    total_summary_row = int(inputs[cc]); cc = cc+1
    tasks = inputs[cc]; cc = cc+1
    only_raw = inputs[cc]; cc = cc+1
    perform_user_based_sorting = inputs[cc]; cc = cc+1
    do_sorting_based_on = inputs[cc]; cc = cc+1
    orderOFsorting = inputs[cc]; cc = cc +1
    window_x = int(inputs[cc]); cc = cc +1
    window_y = int(inputs[cc])
    #==============================================================================================================================
    #                                         PART 1: sorting out based on user configuration
    #==============================================================================================================================
    alg, dates, imgTgs, jbIDs, sorting_based_on_this_col = read_csv_file(path_to_csv, do_sorting_based_on)
    dict_imgtgs_sortingcol = mkDict_imgTgs_sortingCol(imgTgs, sorting_based_on_this_col)
    read_existing_algorithms(alg, tasks)
    unique_dates = read_dates(dates)
    out_Dict_sorted, out_Dict = read_image_names(imgTgs, unique_dates)

    if str2bool(perform_user_based_sorting) is True:
        series = pd.Series(dict_imgtgs_sortingcol)
        if orderOFsorting.lower() in ("ascending"):
            series.sort_values(axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last', ignore_index=False, key=None)
        elif orderOFsorting.lower() in ("descending"):
            series.sort_values(axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last', ignore_index=False, key=None)
        out_Dict_sorted = list(series.to_dict().keys())
        out_Dict_sorted = [x.split(slideFormat)[0] for x in out_Dict_sorted]
    #==============================================================================================================================
    #                                         PART 2: show images for mass review
    #==============================================================================================================================
    
    x = window_x
    y = window_y
    ratio = 4
    
    fig = plt.figure(figsize=(x,y))
    
    if str2bool(only_raw) is not True:
        total_summary = total_summary_col*total_summary_row
        usertasks = len(tasks.split(','))
        alltasks = len(out_Dict_sorted)*usertasks
        walls = math.floor(alltasks/total_summary) + 1
        block = 1; iter = 1; case = 2; tsk0 = 0; rng1 = 2; filled = 0
        for key in out_Dict_sorted:
            value = out_Dict[key]
            if filled < total_summary and (block-1)*total_summary+filled < alltasks:
                print(value)
                case, tsk0, iter = do_plotting(value, ratio, total_summary_row, total_summary_col,iter, tsk0, case, tasks, only_raw)
                filled = filled + usertasks

            elif block<walls and filled >= total_summary:                
                # Save the full figure
                if not os.path.exists(os.path.join(output_dir,'massReview_'+ study_name)):
                    os.mkdir(os.path.join(output_dir, 'massReview_'+ study_name))
                rng2 = case -1
                fig.savefig(os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format), bbox_inches='tight', pad_inches=0)
                print('saved the results to '+ os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format))
                fig = plt.figure(figsize=(x,y))
                rng1 = rng2 + 1
                iter = 1
                block = block+1
                filled = 0
                print(value)
                case, tsk0, iter = do_plotting(value, ratio, total_summary_row, total_summary_col,iter, tsk0, case, tasks, only_raw)
                filled = filled + usertasks
        if block==walls and (block-1)*total_summary+filled == alltasks:              
            # Save the full figure
            if not os.path.exists(os.path.join(output_dir,'massReview_'+ study_name)):
                os.mkdir(os.path.join(output_dir, 'massReview_'+ study_name))
            rng2 = case -1
            fig.savefig(os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format), bbox_inches='tight', pad_inches=0)
            print('saved the results to '+ os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format))    


    elif str2bool(only_raw) is True:
        total_summary = total_summary_col*total_summary_row
        usertasks = 1
        alltasks = len(out_Dict_sorted)*1
        walls = math.floor(alltasks/total_summary) + 1
        block = 1; iter = 1; case = 2; tsk0 = 0; rng1 = 2; filled = 0
        for key in out_Dict_sorted:
            value = out_Dict[key]
            if filled < total_summary and (block-1)*total_summary+filled < alltasks:
                print(value)
                case, tsk0, iter = do_plotting(value, ratio, total_summary_row, total_summary_col,iter, tsk0, case, tasks, only_raw)
                filled = filled + 1

            elif block<walls and filled >= total_summary:                
                # Save the full figure
                if not os.path.exists(os.path.join(output_dir,'massReview_'+ study_name)):
                    os.mkdir(os.path.join(output_dir, 'massReview_'+ study_name))
                rng2 = case -1
                fig.savefig(os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+'_OnlyRaw'+output_format), bbox_inches='tight', pad_inches=0)
                print('saved the results to '+ os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format))
                fig = plt.figure(figsize=(x,y))
                rng1 = rng2 + 1
                iter = 1
                block = block+1
                filled = 0
                print(value)
                case, tsk0, iter = do_plotting(value, ratio, total_summary_row, total_summary_col,iter, tsk0, case, tasks, only_raw)
                filled = filled + 1
        if block==walls and (block-1)*total_summary+filled == alltasks:              
            # Save the full figure
            if not os.path.exists(os.path.join(output_dir,'massReview_'+ study_name)):
                os.mkdir(os.path.join(output_dir, 'massReview_'+ study_name))
            rng2 = case -1
            fig.savefig(os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+'_OnlyRaw'+output_format), bbox_inches='tight', pad_inches=0)
            print('saved the results to '+ os.path.join(output_dir, 'massReview_'+ study_name, study_name + '_range_'+str(rng1)+'-'+str(rng2)+output_format))    

    
    now2 = datetime.datetime.now()
    print("now =", now2)
    print(now2-now1)
    print('******* FINISHED ******')