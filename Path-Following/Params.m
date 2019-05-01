classdef Params < handle
    
    %% Properties
    properties (SetAccess = private)
        maxIter = 100;    % Maximum number of iterations allowed
        tol     = 1.e-8;  % Convergence tolerance
        verbose = 2;      % Controlls how much information to dispaly.
        % 0   : Nothing
        % 1   : Only optimal information
        % 2   : every iteration + optimal information
        % >=3 : All information
    end
    
    properties (Constant)
        maxDiag = 5.e+15; % Cap for element in the X^{-1}S matrix
        etaMin  = .995;   % Minimum value of the steplength scale parameter eta
    end
    
    %% Methods
    methods
        %% Constructor
        function params = Params(parameters)
            if nargin > 0
                if isfield(parameters, 'maxIter')
                    params.maxIter = parameters.maxIter;
                end
                
                if isfield(parameters, 'tol')
                    params.tol = parameters.tol;
                end
                
                if isfield(parameters, 'verbose')
                    params.verbose = parameters.verbose;
                end
            end
        end
    end
end