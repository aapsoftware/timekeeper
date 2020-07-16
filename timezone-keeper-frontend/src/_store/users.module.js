import { userService } from '../_services';

const state = {
    user: {},
    status: {}
};

const actions = {
    getUserDetails({ commit }) {
        commit('getUserDetailsRequest');
        userService.getUserDetails()
            .then(
                user => commit('getUserDetailsSuccess', user),
                error => commit('getUserDetailsFailure', error)
            );
    },
    updateUserDetails({ dispath, commit }, userDetails) {
        commit('updateUserDetailsRequest');
        userService.updateUserDetails(userDetails)
            .then(
                user => {
                    commit('updateUserDetailsSuccess', userDetails);
                    dispatch('alert/success', 'Account updated successfully', { root: true });
                },
                error => {
                    commit('updateUserDetailsFailure', error);
                    dispatch('alert/error', error, { root: true });
                }
            );
    }
};

const mutations = {
    getUserDetailsRequest(state) {
        state.status = { loadingUserDetails: true };
    },
    getUserDetailsSuccess(state, user) {
        state.user = user;
        state.status = { loadedUserDetails: true };
    },
    getUserDetailsFailure(state, error) {
        state.status = { error };
    },
    updateUserDetailsRequest(state) {
        state.status = { updatingUserDetails: true };
    },
    updateUserDetailsSuccess(state, user) {
        state.user = {
            ...state.user,
            ...user
        }
        state.status = { updatedUserDetails: true };
    },
    updateUserDetailsFailure(state, error) {
        state.status = { error };
    }
};

export const users = {
    namespaced: true,
    state,
    actions,
    mutations
};
