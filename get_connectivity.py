def get_connectivity(source_abb,targ_abb,ontology,mcc):
    '''
    Maps the connectivity between two structures of interest.
    Inputs:
        source_abb (str): abbreviation for the source structure.
        targ_abb (str): abbreviation for the target structure.
    Outputs:
        unionizes (dict): a dictionary of pandas tables for all the experiments where the source injections 
            resulted in expression within the target structure. Keys are the experiment IDs.
        npv (dict): a dictionary where the keys are the experiment IDs and the values are the 
            normalized projection volume of the source injection within the target structure.
    '''
    
    # get structure IDs
    source_ID = ontology.df[ontology.df.acronym==source_abb].id.values[0]
    targ_ID = ontology.df[ontology.df.acronym==targ_abb].id.values[0]
    
    # pull source experiments
    source = mcc.get_experiments(dataframe=True, injection_structure_ids=[source_ID])

    # identify all experiments with injections from source
    source_exp_IDs = list(source.id.values)
    
    unionizes = mcc.get_structure_unionizes(source.id.values, structure_ids=[source_ID,targ_ID])

    filtered_projection_data = unionizes[(unionizes.hemisphere_id == 3) &
                                         (unionizes.is_injection==False) &
                                        (unionizes.structure_id == targ_ID)]
    filtered_injection_data = unionizes[(unionizes.hemisphere_id == 3) &
                                         (unionizes.is_injection==True) &
                                        (unionizes.structure_id == source_ID)]
     
    return filtered_injection_data, filtered_projection_data




# get average injection (weighted and unweighted) densities 
def get_mean_injection_density(injection,projection,mcc):

    injd_unweight=0
    injd_weight=0
    
    exp_IDs = list(injection.experiment_id)
    npv_i = list(injection.normalized_projection_volume)
    npv_p = list(projection.normalized_projection_volume)
    
    for i in range(len(exp_IDs)):
        cid=exp_IDs[i]
        injd, _ = mcc.get_injection_density(cid)
        # Use normalized injection volume at the injection site 
        # to normalize the injection density importance (assuming
        # we should treat injections with lots of outside contamination
        # as less important)
        injd*=npv_i[i]
        # get the unweighted sum of injection densities
        injd_unweight += injd
        # now get the sum, weighted by the normalized injection volume at 
        # at the target structure
        injd_weight += injd*npv_p[i]
    
    injd_unweight = injd_unweight / len(exp_IDs)
    injd_weight = injd_weight / len(exp_IDs)
    
    return injd_unweight, injd_weight



def plot_max_voxels(X, ontology, mcc, mask_abbr=None, close_buffer=50):
    if mask_abbr is not None:
        mask_id = ontology.df[ontology.df.acronym==mask_abbr].id.values[0]
        mask, _ = mcc.get_structure_mask(mask_id)
        X=X*mask
        mask=mask.astype(float)
        mask[mask==0]=np.nan
        
    # get whole brain template
    template, template_info = mcc.get_template_volume()

    mX_a1 = X.max(axis=1)
    mXx_a1 = np.unravel_index(mX_a1.argmax(),mX_a1.shape);
    mX_a1[mX_a1==0]=np.nan

    mX_a2 = X.max(axis=0)
    mXx_a2 = np.unravel_index(mX_a2.argmax(),mX_a2.shape);
    mX_a2[mX_a2==0]=np.nan

    mX_a3 = X.max(axis=2)
    mXx_a3 = np.unravel_index(mX_a3.argmax(),mX_a3.shape);
    mX_a3[mX_a3==0]=np.nan

    # plotting
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(nrows=3, ncols=2, figsize=(10, 15)) 

    ax1.imshow(template[:,mXx_a2[0],:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax1.imshow(mask[:,mXx_a2[0],:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax1.imshow(mX_a1, cmap='hot', aspect='equal')
    ax1.set_title('Horizontal view')
    ax2.imshow(template[:,mXx_a2[0],:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax2.imshow(mask[:,mXx_a2[0],:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax2.imshow(mX_a1, cmap='hot', aspect='equal')
    ax2.set_title('Horizontal view, zoomed')
    ax2.set_ylim(mXx_a1[0]+close_buffer,mXx_a1[0]-close_buffer)
    ax2.set_xlim(mXx_a1[1]-close_buffer,mXx_a1[1]+close_buffer)

    ax3.imshow(template[mXx_a1[0],:,:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax3.imshow(mask[mXx_a1[0],:,:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax3.imshow(mX_a2, cmap='hot', aspect='equal')
    ax3.set_title('Coronal view')
    ax4.imshow(template[mXx_a1[0],:,:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax4.imshow(mask[mXx_a1[0],:,:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax4.imshow(mX_a2, cmap='hot', aspect='equal')
    ax4.set_title('Coronal view, zoomed')
    ax4.set_ylim(mXx_a2[0]+close_buffer,mXx_a2[0]-close_buffer)
    ax4.set_xlim(mXx_a2[1]-close_buffer,mXx_a2[1]+close_buffer)

    ax5.imshow(template.T[mXx_a2[1],:,:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax5.imshow(mask[mXx_a2[1],:,:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax5.imshow(mX_a3.T, cmap='hot', aspect='equal')
    ax5.set_title('Saggittal view')
    ax6.imshow(template.T[mXx_a2[1],:,:], cmap='gray', aspect='equal', vmin=template.min(), vmax=template.max())
    if mask_abbr is not None:
        ax6.imshow(mask[mXx_a2[1],:,:], cmap='cool', aspect='equal', vmin=template.min(), vmax=template.max())
    ax6.imshow(mX_a3.T, cmap='hot', aspect='equal')
    ax6.set_title('Saggittal view, zoomed')
    ax6.set_ylim(mXx_a2[0]+close_buffer,mXx_a2[0]-close_buffer)
    ax6.set_xlim(mXx_a1[0]-close_buffer,mXx_a1[0]+close_buffer)

