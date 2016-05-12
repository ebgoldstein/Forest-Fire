%FOREST FIRE MODEL
%
%This code was written to implement the cellular automata model of forest
%fires (Bak et al. 1990, Drossel and Schwabl 1992)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%
%INPUTS:
% The main adjustable parameters are
%   1) 'Dimensions' - sets the size of the computational domain)
%   2) 'ProbGrow' - sets the probability that a forest will grow in a cell
%       that is unoccupied.
%   3) 'ProbLight' - sets the probability that a forest with no burning
%       neighbors will ignite ('Lightning' rule; Drossel and Schwabl 1992)
%   4) 'MooreNeighborhood' - 'Y' means 8-cell Moore neighborhood, 'N' means
%       4-cell 'von Neumann' neighborhood.
%
%   Theoretical Considerations regarding the inputs:
%
%-(ProbGrow/ProbLight) can be thought of as the average number of trees
%   planted between two lightining strikes
%
%-When (ProbLight << ProbGrow << 1) then large clusters develop (SOC state)
%
%-Forest density approaches a constant of ~0.39 when ProbLight -> 0.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%OUPUTS:
%  The output is 1 figure with 2 (time evolving) plots
%    1) The first shows the computational domain, with empty cells, trees,
%      and fires (colorcoded).
%    2)The second is the percentage of land occupied by empty cells, trees,
%      and fires at a given time
%
%There is a set of lines at the bottom that can be
%commented/uncommented to save a '*.avi' movie of the evolving plots.
%
%Also as output is the 3D array 'TS' which shows the matrix for each time
%step so code can be debugged, statistics can be calculated, and further
%moves can be made. The X and Y dimension of the array TS=(X,Y,Z) are the
%computational domain for each time step Z.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%ISSUES:
%   a)Neighborhood routine could be better with convolution
%       1) von Neumann neighborhood is not implemented for lightning rule
%   b)Open NOT periodic BCs.
%   c)I haven't tested to see if i get the same behavior as Bak et al 1990
%   d)An Immunity rule could be implemented (Drossel and Schwabl
%       Physica D 199, 183?197 1993) or Yoder, Turcotte, and Rundle,
%       Physical Review E 2011
%   e)A Human ignition rule could be implemented: Krenn and Hergarten 2009
%       Nat. Hazards Earth Syst. Sci., 9, 1743?1748
%
%No spatial stats are extracted, and i use an IC that is different from Bak
%et al.: I use a mix of forest+fire+bare ground as opposed to only
%forest+fire.. I suspect the Bak et al. 1990 IC doesn;t work in this
%implementation b/c I don't have periodic BCs, so fires tend to be
%extinguished on the edges..
%
%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%REFERENCES
%
%Bak, P, Chen K., and Tang, C, 1990, A forest-fire model and some thoughts
%on turbulence, Physics Letters A, 147(5-6), 297-300.
%
%Drossel, B and Schwabl F, 1992, Self Organized Critical Forest-Fire model
%Phys. Rev. Lett. 69, 1629 (1992).
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%"It is easier to write a new code than to understand an old one"
%-John von Neumann to Marston Morse, 1952
%
%Written by EBG 11/9/2013
%
%%The MIT License (MIT)
%Copyright (c) 2016 Evan B. Goldstein
%

clear all
close all
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%PARAMETER TO ADJUST
Dimensions=100; %Bak et al. 1990 used 256

%Probabiliy that a forest will grow in an unoccupied cell
%(btwn 0 (never grow) and 1 (always grow))
ProbGrow=0.01;

%Probabiliy that a lightning will ignite a forest with no burning neighbors
%(btwn 0 (never) and 1 (always))
%Set to 0 ito turn Drossel Schwabl 1992 Lightning rule off.
ProbLight=0.00001;


%Use if Moore Neighborbood (8 cells)? or just von Neumann (4 cells)?
%'Y' or 'N'
MooreNeighborbood='Y';

TMAX=1000;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%initial condition
x=round(rand(Dimensions,Dimensions)*2);

% %Bak et al IC
% x=round(rand(Dimensions,Dimensions))+1;

%0= empty
%1= trees
%2= fire

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%Main loop
for t=1:TMAX

    %%%%%%%%%%%%%%%%%%%%%%%%
    %reset the grid for a new timestep
    xi=x;
    x=zeros(Dimensions,Dimensions);


    %save only the trees: fires burn out and bare patches are saved
    %automatically because x is a matrix of zeros
    x(xi==1)=1;

    %%%%%%%%%%%%%%%%%%%%%%
    %RULE ONE=trees grow with probability p from empty cells
    p=rand(Dimensions,Dimensions);

    x(xi==0 & p<ProbGrow)=1;

    %%%%%%%%%%%%%%%%%%%%%%
    %RULE TWO=trees on fire burn down at next time step
    %Actually I don't implement this rule because the reset of x does it
    %for me.

    %%%%%%%%%%%%%%%%%%%%%%
    %RULE THREE=fire spreads to NN trees at next time step. (this is
    %sloppy, but i needed a quick solution)

        %This is where I could implement the Periodic BCs

    for m=2:Dimensions-1;
        for n=2:Dimensions-1;
            if xi(m,n)==2
                if xi(m-1,n)==1;
                    x(m-1,n)=2;
                end
                if xi(m,n+1)==1;
                    x(m,n+1)=2;
                end
                if xi(m,n-1)==1;
                    x(m,n-1)=2;
                end
                if xi(m+1,n)==1;
                    x(m+1,n)=2;
                end

                if MooreNeighborbood=='Y';
                    if xi(m-1,n-1)==1;
                        x(m-1,n-1)=2;
                    end

                    if xi(m-1,n+1)==1;
                        x(m-1,n+1)=2;
                    end
                    if xi(m+1,n+1)==1;
                        x(m+1,n+1)=2;
                    end
                    if xi(m+1,n-1)==1;
                        x(m+1,n-1)=2;
                    end
                end
            end
        end
    end

    %%%%%%%%%%%%%%%%%%%%%%
    %RULE Four=Tree with no burning neighbors is ignited with probability f

    if ProbLight>0;
        for m=2:Dimensions-1;
            for n=2:Dimensions-1;
                if xi(m,n)==1 && xi(m-1,n)~=2 && xi(m,n+1)~=2 && ...
                        xi(m,n-1)~=2 && xi(m+1,n)~=2 && xi(m-1,n-1)~=2 && ...
                        xi(m-1,n+1)~=2 && xi(m+1,n+1)~=2 && xi(m+1,n-1)~=2;
                    q=rand;
                    if q<ProbLight;
                        x(m,n)=2;
                    end
                end
            end
        end
    end

    %%%%%%%%%%%%%%%%%%%%%
    %Calculate how much land is occupied by fires, bare ground and forest
    Fires=sum(sum(x==2));
    Bare=sum(sum(x==0));
    Forest=sum(sum(x==1));

    FRatio=100*Fires/(Dimensions*Dimensions);
    BRatio=100*Bare/(Dimensions*Dimensions);
    ForRatio=100*Forest/(Dimensions*Dimensions);
    %%%%%%%%%%%%%%%%%%%%%
    %save the computation domain
    TS(:,:,t)=x;
    %%%%%%%%%%%%%%%%%%%%%
    %PLOTS

    %P1: the computational Domain
    subplot(3,1,1:2)
    imagesc(x)
    colormap([1,1,1;0,1,0;1,0,0])
    h = colorbar;
    caxis([0 2])
    title( sprintf( 'ProbGrow= %f, ProbLight= %f', ProbGrow, ProbLight ) )
    %title('ProbLight=' ProbLight)
    set(h, 'YLim', [0 2],'YTick',0.5:0.5:1.5,'YTickLabel',{'empty','trees','fire'})
    axis square

    %P2: Percentage of land occupied by each 'state'
    subplot(3,1,3)
    scatter(t,FRatio,'r*')
    hold on
    scatter(t,ForRatio,'g*')
    scatter(t,BRatio,'k*')
    axis([0 TMAX 0 100])
    legend('Fire','Forest','Bare Ground')
    xlabel('Time (generations)')
    ylabel('% of Area')

    %Save the figure for a movie
    %M(t) = getframe; %Capture the movie frame

    %if routine is going to fast, uncomment the below line
    pause(.0001)  %so can see movie more clearly

    %This gets you out of the Loop if there are no fires (and none will be
    %ignited)
    if ProbLight==0 && Fires==0;
       Error('There are no more Fires to be had!!!')
    end
end

% %UNCOMMENT THIS TO MAKE  MOVIE
% movie(M)
% movie2avi(M,['ForestFire'])
